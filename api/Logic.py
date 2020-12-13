from question_classifier import *
from question_parser import *
from answer_search import *

import time
import json

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

#----------------------------------------Siamens Model--------------------------------------------------------
def load_siamese_model():
	json_file = open('models/model.json','r')
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

def find_if_duplicate_questions(ques1, ques2):
	tokenizer = Tokenizer(num_words=100000)
	with open('models/dictionary.json', 'r') as dictionary_file:
	    dictionary = json.load(dictionary_file)
	MAX_SEQUENCE_LENGTH = 130
	q1_word_seq = convert_text_to_index_array(ques1,dictionary)
	q1_word_seq = [q1_word_seq]
	q2_word_seq = convert_text_to_index_array(ques2,dictionary)
	q2_word_seq = [q2_word_seq]
	q1_data = pad_sequences(q1_word_seq, maxlen=MAX_SEQUENCE_LENGTH)
	q2_data = pad_sequences(q2_word_seq, maxlen=MAX_SEQUENCE_LENGTH)
	model = load_siamese_model()
	# print("Model loaded...")
	pred = model.predict([q1_data, q2_data])
	return pred
	# print(pred)
	# if(pred > 0.5):
	# 	print("Not Duplicate.")
	# else:
	# 	print("duplicate.")

#--------------------------------------End Siamens Model------------------------------------------------------

def find_similar_question (sent):
	with open('data/questions.json', encoding='utf-8', errors='ignore') as f:
		# data = json.load(f)
		dt_questions = json.load(f)
		scores = []
		for i in range(10):
			question = dt_questions[i]['question']
			score = find_if_duplicate_questions(sent, question)
			scores.append(score)
		mn = 9999
		for i in range(len(scores)):
			if scores[i] < mn:
				mn = i
		question = dt_questions[mn]['question']
		answer = dt_questions[mn]['answer']
		return question, answer

class ChatBotGraph:
	def __init__(self):
		self.classifier = QuestionClassifier()
		self.parser = QuestionParser()
		self.searcher = AnswerSearcher()

	def chat_main(self, sent):
		answer = "Hello, I am Aarogya Bot. How can I help you?"
		res_classify = self.classifier.classify(sent)
		
		if not res_classify:
			question, stage2_answer = find_similar_question(sent)
			return "I don't know if I fully understand the question, but here's what I found: " + stage2_answer
			# return answer
		res_sql = self.parser.parser_main(res_classify)
		
		final_answers = self.searcher.search_main(res_sql)
		
		if not final_answers:
			#Perform Stage 2: Using Datasets by checking question similarity in a loop and extracting answer from least score
			question, stage2_answer = find_similar_question(sent)
			return "I don't know if I fully understand the question, but here's what I found: " + stage2_answer
			# return answer
		else:
			return '\n'.join(final_answers)
		
