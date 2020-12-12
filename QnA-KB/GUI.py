from question_classifier import *
from question_parser import *
from answer_search import *

from tkinter import *
from PIL import ImageTk, Image
import time


class ChatBotGraph:
	def __init__(self):
		self.classifier = QuestionClassifier()
		self.parser = QuestionParser()
		self.searcher = AnswerSearcher()

	def chat_main(self, sent):
		answer = "Hello, I am Aarogya Bot. How can I hope I can help you?"
		res_classify = self.classifier.classify(sent)
		#print(res_classify)
		if not res_classify:
			return answer
		res_sql = self.parser.parser_main(res_classify)
		#print("Resultant SQL: ", res_sql)
		final_answers = self.searcher.search_main(res_sql)
		#print("Final Answer", final_answers)
		if not final_answers:
			return answer
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