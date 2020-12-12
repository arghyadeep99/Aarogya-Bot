from flask import Flask, request
from Logic import ChatBotGraph

app = Flask(__name__)

@app.route("/")
def home():
    handler = ChatBotGraph()
    return "API Starts here\n-------\nSearch term: " + request.args.get('search', '') + "\n" + handler.chat_main(request.args.get('search', ''))

