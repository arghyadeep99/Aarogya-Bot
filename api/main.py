from flask import Flask, request
from Logic import ChatBotGraph
import json

app = Flask(__name__)

@app.route("/")
def home():
    handler = ChatBotGraph()
    search_term = request.args.get('search', '')

    data = {
        "search": search_term,
        "message": handler.chat_main(search_term)
    }

    return json.dumps(data)
