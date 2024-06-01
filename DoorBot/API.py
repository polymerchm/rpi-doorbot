import os
from redis import Redis
from flask import Flask, request, jsonify, Response


ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

def create_app():
    app = Flask(__name__)
    


    


