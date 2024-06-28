
"""

DoorBot RESTful API
allows interogation of the DoorBot and remotely unlocking it

"""

from redis import Redis
from flask import Flask, request, jsonify, Response
import sys, signal, os
import DoorBot.Config as Config
from flask import Flask, request, jsonify, abort, render_template, Response
from flask_cors import CORS, cross_origin
from flask_httpauth import HTTPBasicAuth
from DoorBot.constants import *
from flask_stache import render_template


DEBUG = Config.get('DEBUG')

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

def create_app():
    app = Flask(__name__, static_url_path='/static', template_folder=os.path.join(ROOT_PATH,'templates'))
    return app

app = create_app()
CORS(app)

redis_cli = Redis()

def redisGet(key: str, default:any="unset") -> any:
    result = redis_cli.get(key)
    return result if result != None else default


@app.route('/unlock', methods=['POST'])
def unlock():
    redis_cli.publish(DOOR_LOCK,'unlock')

@app.route('/lock', methods=['POST'])
def lock():
    redis_cli.publish(DOOR_LOCK,'lock')

@app.route('/', methods=['GET'])
@app.route('/status', methods=['GET'])
def status():
    args = {
            'door': redisGet(DOOR_STATE), 
            'lock': redisGet(DOOR_LOCK),
            'location':redisGet(LOCATION),
            'serialnumber':redisGet(SERIAL_NUMBER),
            'cachesize':redis_cli.llen(FOB_LIST),
            'lastrefresh':redisGet(LAST_FOB_LIST_REFRESH),
            'lastreboot':redisGet(REBOOT_TIME),
    }
    return render_template('index', **args)



if __name__== '__main__':
    app.run(debug=True) #use with vscode
