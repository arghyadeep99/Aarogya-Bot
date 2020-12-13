###############################
## IMPORTS
###############################

import pandas as pd
import numpy as np
import re

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils import np_utils
from keras.layers.embeddings import Embedding
from keras.utils.data_utils import get_file
from keras.models import Model
from keras.layers import Input, Embedding, LSTM, Merge, Dropout, concatenate, Dense, BatchNormalization, Lambda, TimeDistributed, Dot, dot
import keras.backend as K
from keras.optimizers import Adadelta
from keras.callbacks import ModelCheckpoint


from sklearn.model_selection import train_test_split

from zipfile import ZipFile
from os.path import expanduser, exists

import datetime
import time


###############################
## Read Data
###############################


train_dataset = pd.read_csv('train.csv')
train_df = train_dataset.copy()


q1_list = train_df['question1'].tolist()
q1_list = [str(ques) for ques in q1_list]
q2_list = train_df['question2'].tolist()
q2_list = [str(ques) for ques in q2_list]
is_duplicate_list = train_df['is_duplicate'].tolist()


###############################
## Make word sequences 
###############################

all_questions_list = q1_list + q2_list
tokenizer = Tokenizer(num_words=100000)
tokenizer.fit_on_texts(all_questions_list)

q1_word_seq = tokenizer.texts_to_sequences(q1_list)
q2_word_seq = tokenizer.texts_to_sequences(q2_list)
word_index = tokenizer.word_index

###############################
## Download and initialize Glove Embeddings
###############################

GLOVE_DOWNLOAD_URL = 'http://nlp.stanford.edu/data/glove.840B.300d.zip'

if not exists(expanduser('~/.keras/datasets/glove.840B.300d.zip')):
    zipfile = ZipFile(get_file('glove.840B.300d.zip', GLOVE_DOWNLOAD_URL))
    zipfile.extract('glove.840B.300d.txt', path=expanduser('~/.keras/datasets/'))
    
print("Processing", 'glove.840B.300d.txt')

embeddings_index = {}

with open(expanduser('~/.keras/datasets/glove.840B.300d.txt'), encoding='utf-8') as f:
    for line in f:
        values = line.split(' ')
        word = values[0]
        embedding = np.asarray(values[1:], dtype='float32')
        embeddings_index[word] = embedding

###############################
## Create word embeddings
###############################

MAX_NB_WORDS = 100000
EMBEDDING_DIM = 300

nb_words = min(MAX_NB_WORDS, len(word_index))
word_embedding_matrix = np.zeros((nb_words + 1, EMBEDDING_DIM))
for word, i in word_index.items():
    if i > MAX_NB_WORDS:
        continue
    embedding_vector = embeddings_index.get(word)
    if embedding_vector is not None:
        word_embedding_matrix[i] = embedding_vector


###############################
## Create training & validation data
###############################

MAX_SEQUENCE_LENGTH = 30

q1_data = pad_sequences(q1_word_seq, maxlen=MAX_SEQUENCE_LENGTH)
q2_data = pad_sequences(q2_word_seq, maxlen=MAX_SEQUENCE_LENGTH)
labels = np.array(is_duplicate_list, dtype=int)

X = np.stack((q1_data, q2_data), axis=1)
y = labels
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
Q1_train = X_train[:,0]
Q2_train = X_train[:,1]
Q1_test = X_test[:,0]
Q2_test = X_test[:,1]


###############################
## Siamese Model
###############################


NUM_HIDDEN_UNITS_LAYER1 = 50
NUM_HIDDEN_UNITS_LAYER2 = 100

question1 = Input(shape=(MAX_SEQUENCE_LENGTH,))
question2 = Input(shape=(MAX_SEQUENCE_LENGTH,))

embedding_layer = Embedding(nb_words + 1, 
                 EMBEDDING_DIM, 
                 weights=[word_embedding_matrix], 
                 input_length=MAX_SEQUENCE_LENGTH, 
                 trainable=False)

q1 = embedding_layer(question1)
q2 = embedding_layer(question2)

lstm_first = LSTM(NUM_HIDDEN_UNITS_LAYER1, return_sequences=False)

q1 = lstm_first(q1)
q2 = lstm_first(q2)

dropout_layer = Dropout(0.2)

q1 = dropout_layer(q1)
q2 = dropout_layer(q2)

dense = Dense(100, activation='relu')
dropout_two = Dropout(0.2)
bn_one = BatchNormalization()

q1 = dense(q1)
# q1 = dropout_two(q1)
# q1 = bn_one(q1)
q2 = dense(q2)
# q2 = dropout_two(q2)
# q2 = bn_one(q2)

merged = concatenate([q1,q2])
is_duplicate = Dense(1, activation='sigmoid')(merged)

model = Model(inputs=[question1,question2], outputs=is_duplicate)

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

##############################################################
## Train the model and save checkpoint
##############################################################

print("Starting training at", datetime.datetime.now())
t0 = time.time()
callbacks = [ModelCheckpoint('question_pairs_weights_type1.h5', monitor='val_acc', save_best_only=True)]
history = model.fit([Q1_train, Q2_train],
                    y_train,
                    epochs=25,
                    validation_data=([Q1_test, Q2_test], y_test),
                    verbose=1,
                    batch_size=512,
                    callbacks=callbacks)
t1 = time.time()
print("Training ended at", datetime.datetime.now())
print("Minutes elapsed: %f" % ((t1 - t0) / 60.))
print("Training done.")