from time import time
import pandas as pd
from sklearn.model_selection import train_test_split
import keras
from gensim.models import KeyedVectors
from keras.models import Model
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.layers import Input, Embedding, LSTM, Dense, Flatten, Activation, RepeatVector, Permute, Lambda, \
	Bidirectional, TimeDistributed, Dropout, Conv1D, GlobalMaxPool1D
from keras.layers.merge import multiply, concatenate
import keras.backend as K
from util import make_w2v_embeddings, split_and_zero_padding, ManDist
import numpy as np


TRAIN_CSV = './data/train.csv'
print("Loading word2vec model...")
embedding_path = 'GoogleNews-vectors-negative300.bin.gz'
then = time()
embedding_dict = KeyedVectors.load_word2vec_format(embedding_path, binary=True, limit=500000)
now = time()
print(f"Model loaded. Time taken: {now-then} seconds.")

batch_size = 1024
n_epoch = 50
n_hidden = 50
embedding_dim = 300
max_seq_length = 10

def shared_model(_input):
	len_embeddings = len(embeddings)
	embedded = Embedding(len_embeddings, embedding_dim, weights=[embeddings], input_shape=(max_seq_length,), \
						 trainable=False)(_input)

	# Bi-LSTM
	activations = Bidirectional(LSTM(n_hidden, return_sequences=True), merge_mode='concat')(embedded)
	activations = Bidirectional(LSTM(n_hidden, return_sequences=True), merge_mode='concat')(activations)

	# dropout
	activations = Dropout(0.5)(activations)

	# Attention
	attention = TimeDistributed(Dense(1, activation='tanh'))(activations)
	attention = Flatten()(attention)
	attention = Activation('softmax')(attention)
	attention = RepeatVector(n_hidden * 2)(attention)
	attention = Permute([2, 1])(attention)
	sent_representation = multiply([activations, attention])
	sent_representation = Lambda(lambda x_lambda: K.sum(x_lambda, axis=1))(sent_representation)

	# DropOut
	sent_representation = Dropout(0.1)(sent_representation)

	return sent_representation
	
def create_model():
	left_input = Input(shape=(max_seq_length,), dtype='float32')
	right_input = Input(shape=(max_seq_length,), dtype='float32')
	left_sen_representation = shared_model(left_input)
	right_sen_representation = shared_model(right_input)


	man_distance = ManDist()([left_sen_representation, right_sen_representation])
	sen_representation = concatenate([left_sen_representation, right_sen_representation, man_distance])
	similarity = Dense(1, activation='sigmoid')(Dense(2)(Dense(4)(Dense(16)(sen_representation))))
	model = Model(inputs=[left_input, right_input], outputs=[similarity])
	
	return model


def load_model():
	model = create_model()
	model.load_weights('./data/SiameseLSTM.h5')
	return model
	

def find_similar_sentence(user_input):
	is_duplicate = model.predict([split_df['left'], split_df['right']])
	return is_duplicate
	
df_ =  pd.DataFrame([["What are some special cares for someone with a nose that gets stuffy during the night?", "How can I keep my nose from getting stuffy at night?"]], columns=["question1", "question2"])
for q in ['question1', 'question2']:
	df_[q + '_n'] = df_[q]

train_df, embeddings = make_w2v_embeddings(word2vec=embedding_dict, df=df_, embedding_dim=embedding_dim)
split_df = split_and_zero_padding(train_df, max_seq_length)
print(split_df)

assert split_df['left'].shape == split_df['right'].shape

model = load_model()

print("Similarity score: ", find_similar_sentence("lol"))