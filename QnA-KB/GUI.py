from question_classifier import *
from question_parser import *
from answer_search import *

from tkinter import *
from PIL import ImageTk, Image
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
	model.load_weights('models/question_pairs_weights_type1_final.h5')
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
		#print(res_classify)
		if not res_classify:
			question, answer = find_similar_question(sent)
			return f'I don\'t know if I fully understood the question, but here it\'s what I found:\n Similar question: {question}\n{answer}'
			
		res_sql = self.parser.parser_main(res_classify)
		#print("Resultant SQL: ", res_sql)
		final_answers = self.searcher.search_main(res_sql)
		#print("Final Answer", final_answers)
		if not final_answers:
			question, answer = find_similar_question(sent)
			return f'I don\'t know if I fully understood the question, but here it\'s what I found:\n Similar question: {question}\n{answer}'
		else:
			return '\n'.join(final_answers)
		
def main():
	handler = ChatBotGraph()  
	def sendMsg():
		strMsg = 'User:' + time.strftime("%Y-%m-%d %H:%M:%S",
									  time.localtime()) + '\n'
		txtMsgList.insert(END, strMsg, 'greencolor')
		txtMsgList.insert(END, txtMsg.get('0.0', END))
		text = txtMsg.get('0.0', END)
		txtMsg.delete('0.0', END)
		print ("text is "+text)
		
		text2 = handler.chat_main(text) + '\n '
		strMsg2 = 'Aarogya Bot:' + time.strftime("%Y-%m-%d %H:%M:%S",
									  time.localtime()) + '\n'
		txtMsgList.insert(END, strMsg2, 'greencolor')
		txtMsgList.insert(END, text2)
										

	def cancelMsg():
		txtMsg.delete('0.0', END)


	t = Tk()
	t.title('Aarogya Bot')

	frmLT = Frame(width=500, height=320, bg='white')
	frmLC = Frame(width=500, height=150, bg='white')
	frmLB = Frame(width=500, height=30)
	frmRT = Frame(width=300, height=500)

	txtMsgList = Text(frmLT)
	txtMsgList.tag_config('greencolor', foreground='#008C00')
	txtMsg = Text(frmLC);
	btnSend = Button(frmLB, text='Send', width = 8, command=sendMsg)
	btnCancel = Button(frmLB, text='Cancel', width = 8, command=cancelMsg)
	imgInfo = PhotoImage(file = "doctor.gif")
	lblImage = Label(frmRT, image = imgInfo)
	lblImage.image = imgInfo

	frmLT.grid(row=0, column=0, columnspan=2, padx=1, pady=3)
	frmLC.grid(row=1, column=0, columnspan=2, padx=1, pady=3)
	frmLB.grid(row=2, column=0, columnspan=2)
	frmRT.grid(row=0, column=2, rowspan=3, padx=2, pady=3)
	frmLT.grid_propagate(0)
	frmLC.grid_propagate(0)
	frmLB.grid_propagate(0)
	frmRT.grid_propagate(0)
	btnSend.grid(row=2, column=0)
	btnCancel.grid(row=2, column=1)
	lblImage.grid()
	txtMsgList.grid()
	txtMsg.grid()

	t.mainloop()

if __name__ == '__main__':
	main()
