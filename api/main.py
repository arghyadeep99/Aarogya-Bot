from flask import Flask, request
from flask_cors import CORS, cross_origin

from Logic import ChatBotGraph
import json

app = Flask(__name__)
CORS(app)

handler = ChatBotGraph()

@app.route("/")
def home():
    search_term = request.args.get('search', '')

    data = {
        "search": search_term,
        "message": handler.chat_main(search_term)
    }

    return json.dumps(data)
