from keras import backend as K
from keras.layers import Layer
from keras.preprocessing.sequence import pad_sequences
import numpy as np
import itertools
import re


def text_to_word_list(text):
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


def split_and_zero_padding(df, max_seq_length):

	X = {'left': df['question1_n'], 'right': df['question2_n']}

	for dataset, side in itertools.product([X], ['left', 'right']):
		dataset[side] = pad_sequences(dataset[side], padding='pre', truncating='post', maxlen=max_seq_length)

	return dataset


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
