from question_classifier import *
from question_parser import *
from answer_search import *
import tkinter.messagebox

from tkinter import *
from PIL import ImageTk, Image
import time
import pyttsx3
import threading
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


saved_username = ["You"]
window_size="400x400"

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

class ChatInterface(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master

        #sets default bg for top level windows
        self.tl_bg = "#EEEEEE"
        self.tl_bg2 = "#EEEEEE"
        self.tl_fg = "#000000"
        self.font = "Verdana 10"

        menu = Menu(self.master)
        self.master.config(menu=menu, bd=5)
# Menu bar

    # File
        file = Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file)
       # file.add_command(label="Save Chat Log", command=self.save_chat)
        file.add_command(label="Clear Chat", command=self.clear_chat)
      #  file.add_separator()
        file.add_command(label="Exit",command=self.chatexit)

    # Options
        options = Menu(menu, tearoff=0)
        menu.add_cascade(label="Options", menu=options)

        # username
       

        

        # font
        font = Menu(options, tearoff=0)
        options.add_cascade(label="Font", menu=font)
        font.add_command(label="Default",command=self.font_change_default)
        font.add_command(label="Times",command=self.font_change_times)
        font.add_command(label="System",command=self.font_change_system)
        font.add_command(label="Helvetica",command=self.font_change_helvetica)
        font.add_command(label="Fixedsys",command=self.font_change_fixedsys)

        # color theme
        color_theme = Menu(options, tearoff=0)
        options.add_cascade(label="Color Theme", menu=color_theme)
        color_theme.add_command(label="Default",command=self.color_theme_default) 
        color_theme.add_command(label="Grey",command=self.color_theme_grey) 
        color_theme.add_command(label="Blue",command=self.color_theme_dark_blue) 
        color_theme.add_command(label="Torque",command=self.color_theme_turquoise)
        color_theme.add_command(label="Hacker",command=self.color_theme_hacker)


      
        help_option = Menu(menu, tearoff=0)
        menu.add_cascade(label="Help", menu=help_option)
        #help_option.add_command(label="Features", command=self.features_msg)
        help_option.add_command(label="About Aarogya-Bot", command=self.msg)
        help_option.add_command(label="Develpoers", command=self.about)

        self.text_frame = Frame(self.master, bd=6)
        self.text_frame.pack(expand=True, fill=BOTH)

        # scrollbar for text box
        self.text_box_scrollbar = Scrollbar(self.text_frame, bd=0)
        self.text_box_scrollbar.pack(fill=Y, side=RIGHT)

        # contains messages
        self.text_box = Text(self.text_frame, yscrollcommand=self.text_box_scrollbar.set, state=DISABLED,
                             bd=1, padx=6, pady=6, spacing3=8, wrap=WORD, bg=None, font="Verdana 10", relief=GROOVE,
                             width=10, height=1)
        self.text_box.pack(expand=True, fill=BOTH)
        self.text_box_scrollbar.config(command=self.text_box.yview)

        # frame containing user entry field
        self.entry_frame = Frame(self.master, bd=1)
        self.entry_frame.pack(side=LEFT, fill=BOTH, expand=True)

        # entry field
        self.entry_field = Entry(self.entry_frame, bd=1, justify=LEFT)
        self.entry_field.pack(fill=X, padx=6, pady=6, ipady=3)
        # self.users_message = self.entry_field.get()

        # frame containing send button and emoji button
        self.send_button_frame = Frame(self.master, bd=0)
        self.send_button_frame.pack(fill=BOTH)

        # send button
        self.send_button = Button(self.send_button_frame, text="Send", width=5, relief=GROOVE, bg='white',
                                  bd=1, command=lambda: self.send_message_insert(None), activebackground="#FFFFFF",
                                  activeforeground="#000000")
        self.send_button.pack(side=LEFT, ipady=8)
        self.master.bind("<Return>", self.send_message_insert)
        
        self.last_sent_label(date="No messages sent.")
        #t2 = threading.Thread(target=self.send_message_insert(, name='t1')
        #t2.start()
        
    def playResponce(self,response):
        x=pyttsx3.init()
        voices=x.getProperty('voices')
        x.setProperty('voice',voices[2].id)
        #print(responce)
        li = []
        if len(response) > 100:
            if response.find('--') == -1:
                b = response.split('--')
                #print(b)
                 
        x.setProperty('rate',120)
        # x.setProperty('volume',50)
        x.say(response)
        x.runAndWait()
        #print("Played Successfully......")
        
        
    def last_sent_label(self, date):

        try:
            self.sent_label.destroy()
        except AttributeError:
            pass

        self.sent_label = Label(self.entry_frame, font="Verdana 7", text=date, bg=self.tl_bg2, fg=self.tl_fg)
        self.sent_label.pack(side=LEFT, fill=X, padx=3)

    def clear_chat(self):
        self.text_box.config(state=NORMAL)
        self.last_sent_label(date="No messages sent.")
        self.text_box.delete(1.0, END)
        self.text_box.delete(1.0, END)
        self.text_box.config(state=DISABLED)

    def chatexit(self):
        exit()

    def msg(self):
        tkinter.messagebox.showinfo("Aarogya-Bot info")
    def about(self):
        tkinter.messagebox.showinfo("Developers")
    
    def send_message_insert(self, message):
		# strMsg = message	
        self.text_box.tag_config('red', foreground='#ff0000')
        user_input = self.entry_field.get()
        print(user_input)
        pr0 = "Human : "+ time.strftime('%B %d, %Y' + ' at ' + '%I:%M %p') + "\n"
        self.text_box.configure(state=NORMAL)
        self.text_box.insert(END, pr0, "red")
        self.entry_field.delete(0,END)
        self.text_box.configure(state=DISABLED)
        self.text_box.see(END)
        pr1 = user_input + "\n"
        self.text_box.configure(state=NORMAL)
        self.text_box.insert(END, pr1)
        self.entry_field.delete(0,END)
        self.text_box.configure(state=DISABLED)
        self.text_box.see(END)
        text2 = handler.chat_main(user_input) + '\n '
        print(text2)
        strMsg2 = text2
        pr3 = "Aarogya Bot:  : "+ time.strftime('%B %d, %Y' + ' at ' + '%I:%M %p') + "\n"
        self.text_box.configure(state=NORMAL)
        self.text_box.insert(END, pr3, "red")
        self.text_box.configure(state=DISABLED)
        self.text_box.see(END)
        self.text_box.configure(state=NORMAL)
        self.text_box.insert(END, strMsg2)
        self.text_box.configure(state=DISABLED)
        self.text_box.see(END)
        self.last_sent_label(str(time.strftime( "Last message sent: " + '%B %d, %Y' + ' at ' + '%I:%M %p')))
        self.entry_field.delete(0,END)
        time.sleep(0)    
        # ob=chat(user_input)
        # pr="PyBot : " + ob + "\n"
        # self.text_box.configure(state=NORMAL)

        # self.text_box.configure(state=DISABLED)
        # self.text_box.see(END)
        # self.last_sent_label(str(time.strftime( "Last message sent: " + '%B %d, %Y' + ' at ' + '%I:%M %p')))
        # self.entry_field.delete(0,END)
        # time.sleep(0)
        # t2 = threading.Thread(target=self.playResponce, args=(text2, ))
        # t2.start()
        #return ob

    


        
        
    def font_change_default(self):
        self.text_box.config(font="Verdana 10")
        self.entry_field.config(font="Verdana 10")
        self.font = "Verdana 10"

    def font_change_times(self):
        self.text_box.config(font="Times")
        self.entry_field.config(font="Times")
        self.font = "Times"

    def font_change_system(self):
        self.text_box.config(font="System")
        self.entry_field.config(font="System")
        self.font = "System"

    def font_change_helvetica(self):
        self.text_box.config(font="helvetica 10")
        self.entry_field.config(font="helvetica 10")
        self.font = "helvetica 10"

    def font_change_fixedsys(self):
        self.text_box.config(font="fixedsys")
        self.entry_field.config(font="fixedsys")
        self.font = "fixedsys"

    def color_theme_default(self):
        self.master.config(bg="#EEEEEE")
        self.text_frame.config(bg="#EEEEEE")
        self.entry_frame.config(bg="#EEEEEE")
        self.text_box.config(bg="#FFFFFF", fg="#000000")
        self.entry_field.config(bg="#FFFFFF", fg="#000000", insertbackground="#000000")
        self.send_button_frame.config(bg="#EEEEEE")
        self.send_button.config(bg="#FFFFFF", fg="#000000", activebackground="#FFFFFF", activeforeground="#000000")
        #self.emoji_button.config(bg="#FFFFFF", fg="#000000", activebackground="#FFFFFF", activeforeground="#000000")
        self.sent_label.config(bg="#EEEEEE", fg="#000000")

        self.tl_bg = "#FFFFFF"
        self.tl_bg2 = "#EEEEEE"
        self.tl_fg = "#000000"

    # Dark
    def color_theme_dark(self):
        self.master.config(bg="#2a2b2d")
        self.text_frame.config(bg="#2a2b2d")
        self.text_box.config(bg="#212121", fg="#FFFFFF")
        self.entry_frame.config(bg="#2a2b2d")
        self.entry_field.config(bg="#212121", fg="#FFFFFF", insertbackground="#FFFFFF")
        self.send_button_frame.config(bg="#2a2b2d")
        self.send_button.config(bg="#212121", fg="#FFFFFF", activebackground="#212121", activeforeground="#FFFFFF")
       # self.emoji_button.config(bg="#212121", fg="#FFFFFF", activebackground="#212121", activeforeground="#FFFFFF")
        self.sent_label.config(bg="#2a2b2d", fg="#FFFFFF")

        self.tl_bg = "#212121"
        self.tl_bg2 = "#2a2b2d"
        self.tl_fg = "#FFFFFF"

    # Grey
    def color_theme_grey(self):	
        self.master.config(bg="#444444")
        self.text_frame.config(bg="#444444")
        self.text_box.config(bg="#4f4f4f", fg="#ffffff")
        self.entry_frame.config(bg="#444444")
        self.entry_field.config(bg="#4f4f4f", fg="#ffffff", insertbackground="#ffffff")
        self.send_button_frame.config(bg="#444444")
        self.send_button.config(bg="#4f4f4f", fg="#ffffff", activebackground="#4f4f4f", activeforeground="#ffffff")
        #self.emoji_button.config(bg="#4f4f4f", fg="#ffffff", activebackground="#4f4f4f", activeforeground="#ffffff")
        self.sent_label.config(bg="#444444", fg="#ffffff")

        self.tl_bg = "#4f4f4f"
        self.tl_bg2 = "#444444"
        self.tl_fg = "#ffffff"


        self.master.config(bg="#003333")
        self.text_frame.config(bg="#003333")
        self.text_box.config(bg="#669999", fg="#FFFFFF")
        self.entry_frame.config(bg="#003333")
        self.entry_field.config(bg="#669999", fg="#FFFFFF", insertbackground="#FFFFFF")
        self.send_button_frame.config(bg="#003333")
        self.send_button.config(bg="#669999", fg="#FFFFFF", activebackground="#669999", activeforeground="#FFFFFF")
        #self.emoji_button.config(bg="#669999", fg="#FFFFFF", activebackground="#669999", activeforeground="#FFFFFF")
        self.sent_label.config(bg="#003333", fg="#FFFFFF")

        self.tl_bg = "#669999"
        self.tl_bg2 = "#003333"
        self.tl_fg = "#FFFFFF"    

    # Blue
    def color_theme_dark_blue(self):
        self.master.config(bg="#263b54")
        self.text_frame.config(bg="#263b54")
        self.text_box.config(bg="#1c2e44", fg="#FFFFFF")
        self.entry_frame.config(bg="#263b54")
        self.entry_field.config(bg="#1c2e44", fg="#FFFFFF", insertbackground="#FFFFFF")
        self.send_button_frame.config(bg="#263b54")
        self.send_button.config(bg="#1c2e44", fg="#FFFFFF", activebackground="#1c2e44", activeforeground="#FFFFFF")
        #self.emoji_button.config(bg="#1c2e44", fg="#FFFFFF", activebackground="#1c2e44", activeforeground="#FFFFFF")
        self.sent_label.config(bg="#263b54", fg="#FFFFFF")

        self.tl_bg = "#1c2e44"
        self.tl_bg2 = "#263b54"
        self.tl_fg = "#FFFFFF"

 
    

    # Torque
    def color_theme_turquoise(self):
        self.master.config(bg="#003333")
        self.text_frame.config(bg="#003333")
        self.text_box.config(bg="#669999", fg="#FFFFFF")
        self.entry_frame.config(bg="#003333")
        self.entry_field.config(bg="#669999", fg="#FFFFFF", insertbackground="#FFFFFF")
        self.send_button_frame.config(bg="#003333")
        self.send_button.config(bg="#669999", fg="#FFFFFF", activebackground="#669999", activeforeground="#FFFFFF")
        #self.emoji_button.config(bg="#669999", fg="#FFFFFF", activebackground="#669999", activeforeground="#FFFFFF")
        self.sent_label.config(bg="#003333", fg="#FFFFFF")

        self.tl_bg = "#669999"
        self.tl_bg2 = "#003333"
        self.tl_fg = "#FFFFFF"

    # Hacker
    def color_theme_hacker(self):
        self.master.config(bg="#0F0F0F")
        self.text_frame.config(bg="#0F0F0F")
        self.entry_frame.config(bg="#0F0F0F")
        self.text_box.config(bg="#0F0F0F", fg="#33FF33")
        self.entry_field.config(bg="#0F0F0F", fg="#33FF33", insertbackground="#33FF33")
        self.send_button_frame.config(bg="#0F0F0F")
        self.send_button.config(bg="#0F0F0F", fg="#FFFFFF", activebackground="#0F0F0F", activeforeground="#FFFFFF")
        #self.emoji_button.config(bg="#0F0F0F", fg="#FFFFFF", activebackground="#0F0F0F", activeforeground="#FFFFFF")
        self.sent_label.config(bg="#0F0F0F", fg="#33FF33")

        self.tl_bg = "#0F0F0F"
        self.tl_bg2 = "#0F0F0F"
        self.tl_fg = "#33FF33"

    

    # Default font and color theme
    def default_format(self):
        self.font_change_default()
        self.color_theme_default() 



if __name__ == '__main__':
    root=Tk()
    a = ChatInterface(root)
    root.geometry(window_size)
    root.title("Aarogya-Bot")
    handler = ChatBotGraph() 
    root.mainloop()
