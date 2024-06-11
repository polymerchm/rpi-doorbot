
from redis import Redis
from flask import Flask, request, jsonify, Response
import sys, signal, os



ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

def create_app():
    app = Flask(__name__)



app = create_app()


if __name__== '__main__':
    app.run(debug=True) #use with vscode
