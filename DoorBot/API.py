
"""

DoorBot RESTful API
allows interogation of the DoorBot and remotely unlocking it

"""

from redis import Redis
from flask import Flask, Response
import os
import DoorBot.Config as Config
from flask_cors import CORS, cross_origin
from flask_httpauth import HTTPBasicAuth
from DoorBot.constants import *
from flask_stache import render_template
from time import sleep
import json
from flask_sse import sse

DEBUG = Config.get('DEBUG')

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

def create_app():
    app = Flask(__name__, static_url_path='/static', template_folder=os.path.join(ROOT_PATH,'templates'))
    return app

app = create_app()
CORS(app)
CORS(sse)
app.register_blueprint(sse, url_prefix='/stream')
app.config["REDIS_URL"] = "redis://localhost:6379"

redis_cli = Redis()

def redisGet(key: str, default:any="unset") -> any:
    result = redis_cli.get(key)
    return result if result != None else default

@app.route('/toggleLock', methods=['GET'])
def toggleLock():
    lockState = redisGet(LOCK_STATE).decode("utf-8")
    if lockState == 'locked':
        redis_cli.publish(DOOR_LOCK_CHANNEL,'unlock')
    else:
        redis_cli.publish(DOOR_LOCK_CHANNEL, 'lock')
    sse.publish({'message':'update'}, type='doorbot.sse')
    return status()

@app.route('/getStatus', methods=['GET'])
def getStatus():
    lockState = redisGet(LOCK_STATE)
    lockState = lockState if not isinstance(lockState, bytes) else lockState.decode('utf-8')
    doorState = redisGet(DOOR_STATE)
    doorState = doorState if not isinstance(doorState,bytes)  else doorState.decode('utf-8')
    response = Response(
        response=json.dumps({'lockState': lockState, 'doorState': doorState}),
        status=200,  
        mimetype="text/plain")
    return response

@app.route('/doorChange', methods=['GET'])
def doorChange():
    sse.publish({'message':'update'}, type='doorbot.sse')
    return '',200

@app.route('/unlock', methods=['POST'])
def unlock():
    redis_cli.publish(DOOR_LOCK_CHANNEL,'unlock')
    sse.publish({'message':'update'}, type='doorbot.sse')
    return '',200


@app.route('/lock', methods=['POST'])
def lock():
    redis_cli.publish(DOOR_LOCK_CHANNEL,'lock')
    sse.publish({'message':'update'}, type='doorbot.sse')
    return '',200

@app.route('/', methods=['GET'])
@app.route('/status', methods=['GET'])
def status():
    args = {
            'doorState': redisGet(DOOR_STATE), 
            'lockState': redisGet(LOCK_STATE), 
            'location':redisGet(LOCATION),
            'serialnumber':redisGet(SERIAL_NUMBER),
            'cachesize':redis_cli.llen(FOB_LIST),
            'lastrefresh':redisGet(LAST_FOB_LIST_REFRESH),
            'lastreboot':redisGet(REBOOT_TIME),
    }
    return render_template('index', **args)



if __name__== '__main__':
    app.run(debug=True) #use with vscode
