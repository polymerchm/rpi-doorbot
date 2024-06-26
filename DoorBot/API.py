
"""

DoorBot RESTful API
allows interogation of the DoorBot and remotely unlocking it

"""

from redis import Redis
from flask import Flask, request, jsonify, Response
import sys, signal, os
import Config
from flask import Flask, request, jsonify, abort, render_template, Response
from flask_cors import CORS, cross_origin
from flask_httpauth import HTTPBasicAuth
from DoorBot.constants import *
from chevron import render 

DEBUG = Config.get('DEBUG')

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

template_path = 'templates'

def render_template(name, args):
    render(name, args, template_path)

def create_app():
    app = Flask(__name__, static_url_path='/static')

app = create_app()
CORS(app)

redis_cli = Redis()


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
            'door':redis_cli.get(DOOR_STATE), 
            'lock':redis_cli.get(DOOR_LOCK),
            'location':redis_cli.get(LOCATION),
            'serialnumber':redis_cli.get(SERIAL_NUMBER),
            'cachesize':redis_cli.llen(FOB_LIST),
            'lastrefresh':redis_cli.get(LAST_FOB_LIST_REFRESH),
            'lastreboot':redis_cli.get(REBOOT_TIME)
    }

    return render_template('status', args)



if __name__== '__main__':
    app.run(debug=True) #use with vscode
