import pandas as pd
import numpy as np
import re

from keras.preprocessing.text import Tokenizer, text_to_word_sequence
from keras.preprocessing.sequence import pad_sequences
from keras.utils import np_utils
from keras.layers.embeddings import Embedding
from keras.utils.data_utils import get_file
from keras.models import Model
from keras.layers import Input, Embedding, LSTM, Dropout, concatenate, Dense, BatchNormalization, Lambda, TimeDistributed, Dot, dot
import keras.backend as K
from keras.optimizers import Adadelta
from keras.callbacks import ModelCheckpoint
from keras.models import model_from_json


from sklearn.model_selection import train_test_split

from zipfile import ZipFile
from os.path import expanduser, exists

import datetime
import time
import json

import click

@click.group()
def cli():
    """ This is a simple cli tool to predict if two quora sentences are duplicate. """
    pass

def load_siamese_model():
	json_file = open('model.json','r')
	loaded_model_json = json_file.read()
	json_file.close()
	# load model
	model = model_from_json(loaded_model_json)
	# load weights
	model.load_weights('question_pairs_weights_type1_final.h5')
	return model

def convert_text_to_index_array(text, dictionary):
	words = text_to_word_sequence(text)
	wordIndices = []
	for word in words:
	    if word in dictionary:
	        wordIndices.append(dictionary[word])
	    else:
	        print("'%s' not in training corpus; ignoring." %(word))
	return wordIndices

@cli.command()
@click.option('--ques1', help='Give the first question.')
@click.option('--ques2', help='Give the second question.')
def find_if_duplicate_questions(ques1, ques2):
	"""This prints yes if the two input questions are duplicate, else prints no."""
	tokenizer = Tokenizer(num_words=100000)
	with open('dictionary.json', 'r') as dictionary_file:
	    dictionary = json.load(dictionary_file)
	MAX_SEQUENCE_LENGTH = 130
	q1_word_seq = convert_text_to_index_array(ques1,dictionary)
	q1_word_seq = [q1_word_seq]
	q2_word_seq = convert_text_to_index_array(ques2,dictionary)
	q2_word_seq = [q2_word_seq]
	q1_data = pad_sequences(q1_word_seq, maxlen=MAX_SEQUENCE_LENGTH)
	q2_data = pad_sequences(q2_word_seq, maxlen=MAX_SEQUENCE_LENGTH)
	model = load_siamese_model()
	print("Model loaded...")
	pred = model.predict([q1_data, q2_data])
	print(pred)
	if(pred > 0.5):
		print("Not Duplicate.")
	else:
		print("duplicate.")

if __name__ == "__main__":
    cli()
