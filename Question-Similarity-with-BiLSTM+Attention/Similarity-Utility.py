#!/usr/bin/env python
# coding: utf-8

from time import time
import pandas as pd
from sklearn.model_selection import train_test_split
import keras
from gensim.models import KeyedVectors
from keras.models import Model, load_model
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.layers import Input, Layer, Embedding, LSTM, Dense, Flatten, Activation, RepeatVector, Permute, Lambda, Bidirectional, TimeDistributed, Dropout, Conv1D, GlobalMaxPool1D
from keras.layers.merge import multiply, concatenate
import keras.backend as K
from util import make_w2v_embeddings, split_and_zero_padding
import numpy as np

import warnings

embeddings = np.load('./embeddings.npy')
len(embeddings)

batch_size = 1024
n_epoch = 50
n_hidden = 50
embedding_dim = 300
max_seq_length = 10


class ManDist(Layer):

    def __init__(self, **kwargs):
        self.result = None
        super(ManDist, self).__init__(**kwargs)

    def build(self, input_shape):
        super(ManDist, self).build(input_shape)

    def call(self, x, **kwargs):
        self.result = K.exp(-K.sum(K.abs(x[0] - x[1]), axis=1, keepdims=True))
        return self.result

    def compute_output_shape(self, input_shape):
        return K.int_shape(self.result)


def shared_model(_input):
    len_embeddings = 11715
    embedded = Embedding(len_embeddings, embedding_dim, weights=[embeddings], input_shape=(max_seq_length,),                          trainable=False)(_input)

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


# In[6]:


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


# In[7]:


def load_model():
    model = create_model()
    model.load_weights('./data/SiameseLSTM.h5')
    return model



model = load_model()



def split_and_zero_padding(df, max_seq_length):
    import itertools
    from keras.preprocessing.sequence import pad_sequences

    X = {'left': df['question1_n'], 'right': df['question2_n']}

    for dataset, side in itertools.product([X], ['left', 'right']):
        dataset[side] = pad_sequences(dataset[side], padding='pre', truncating='post', maxlen=max_seq_length)

    return dataset


def text_to_word_list(text):
    import re
    text = str(text)
    text = text.lower()
    text = re.sub(r"[^A-Za-z0-9^,!.\/'+-=]", " ", text)
    text = re.sub(r"what's", "what is ", text)
    text = re.sub(r"\'s", " ", text)
    text = re.sub(r"\'ve", " have ", text)
    text = re.sub(r"can't", "cannot ", text)
    text = re.sub(r"n't", " not ", text)
    text = re.sub(r"i'm", "i am ", text)
    text = re.sub(r"\'re", " are ", text)
    text = re.sub(r"\'d", " would ", text)
    text = re.sub(r"\'ll", " will ", text)
    text = re.sub(r",", " ", text)
    text = re.sub(r"\.", " ", text)
    text = re.sub(r"!", " ! ", text)
    text = re.sub(r"\/", " ", text)
    text = re.sub(r"\^", " ^ ", text)
    text = re.sub(r"\+", " + ", text)
    text = re.sub(r"\-", " - ", text)
    text = re.sub(r"\=", " = ", text)
    text = re.sub(r"'", " ", text)
    text = re.sub(r"(\d+)(k)", r"\g<1>000", text)
    text = re.sub(r":", " : ", text)
    text = re.sub(r" e g ", " eg ", text)
    text = re.sub(r" b g ", " bg ", text)
    text = re.sub(r" u s ", " american ", text)
    text = re.sub(r"\0s", "0", text)
    text = re.sub(r" 9 11 ", "911", text)
    text = re.sub(r"e - mail", "email", text)
    text = re.sub(r"j k", "jk", text)
    text = re.sub(r"\s{2,}", " ", text)

    text = text.split()

    return text

def make_w2v_embeddings(word2vec, df, embedding_dim):
    vocabs = {}
    vocabs_cnt = 0

    vocabs_not_w2v = {}
    vocabs_not_w2v_cnt = 0

    for index, row in df.iterrows():
        if index != 0 and index % 1000 == 0:
            print(str(index) + " sentences embedded.")

        for question in ['question1', 'question2']:
            q2n = []
            words = text_to_word_list(row[question])

            for word in words:
                if word not in word2vec and word not in vocabs_not_w2v:
                    vocabs_not_w2v_cnt += 1
                    vocabs_not_w2v[word] = 1
                if word not in vocabs:
                    vocabs_cnt += 1
                    vocabs[word] = vocabs_cnt
                    q2n.append(vocabs_cnt)
                else:
                    q2n.append(vocabs[word])
            df.at[index, question + '_n'] = q2n

    embeddings = 1 * np.random.randn(len(vocabs) + 1, embedding_dim)

    embeddings[0] = 0 

    for index in vocabs:
        vocab_word = vocabs[index]
        if vocab_word in word2vec:
            embeddings[index] = word2vec[vocab_word]
    del word2vec

    return df, embeddings


df_ =  pd.DataFrame([["What are the best career growth technologies for automation engineers apart from automation tools?", "Himalayan or Duke KTM 200 for touring?"]], columns=["question1", "question2"])
for q in ['question1', 'question2']:
    df_[q + '_n'] = df_[q]
df_.head()


train_df, embeddings = make_w2v_embeddings(word2vec=embeddings, df=df_, embedding_dim=embedding_dim)
split_df = split_and_zero_padding(train_df, max_seq_length)
print(split_df)


# In[15]:


assert split_df['left'].shape == split_df['right'].shape


# In[16]:


def find_similar_sentence(user_input):
    is_duplicate = model.predict([split_df['left'], split_df['right']])
    return is_duplicate


# In[17]:


score = find_similar_sentence("hi")


# In[18]:


print("score: ", score)


# In[ ]:




