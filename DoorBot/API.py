
"""

DoorBot RESTful API
allows interogation of the DoorBot and remotely unlocking it

"""

from redis import Redis
from flask import Flask, Response
import click
import os, subprocess, sys
from pwd import getpwnam
import DoorBot.Config as Config
from flask_cors import CORS, cross_origin
from flask_httpauth import HTTPBasicAuth
from DoorBot.constants import *
from flask_stache import render_template
from time import sleep
import json
from flask_sse import sse
import DoorBot.service_templates as service_templates
import DoorBot.script_templates as script_templates
import errno


DEBUG = Config.get('DEBUG')

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

def create_app():
    app = Flask(__name__, static_folder=os.path.join(ROOT_PATH,'static'), template_folder=os.path.join(ROOT_PATH,'templates'))
    return app

app = create_app()
CORS(app)
CORS(sse)
app.register_blueprint(sse, url_prefix='/api/stream')
app.config["REDIS_URL"] = "redis://localhost:6379"

redis_cli = Redis()

def redisGet(key: str, default:any="unset") -> any:
    result = redis_cli.get(key)
    return result if result != None else default

@app.route('/api/toggleLock', methods=['GET'])
def toggleLock():
    lockState = redisGet(LOCK_STATE).decode("utf-8")
    if lockState == 'locked':
        redis_cli.publish(DOOR_LOCK_CHANNEL,'unlock')
    else:
        redis_cli.publish(DOOR_LOCK_CHANNEL, 'lock')
    sse.publish({'message':'update'}, type='doorbot.sse')
    return status()

@app.route('/api/getStatus', methods=['GET'])
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

@app.route('/api/doorChange', methods=['GET'])
def doorChange():
    sse.publish({'message':'update'}, type='doorbot.sse')
    return '',200

@app.route('/api/unlock', methods=['POST'])
def unlock():
    redis_cli.publish(DOOR_LOCK_CHANNEL,'unlock')
    sse.publish({'message':'update'}, type='doorbot.sse')
    return '',200


@app.route('/api/lock', methods=['POST'])
def lock():
    redis_cli.publish(DOOR_LOCK_CHANNEL,'lock')
    sse.publish({'message':'update'}, type='doorbot.sse')
    return '',200

@app.route('/api/botStatus', methods=['GET'])
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

@app.route('/', methods=['GET'])
def index():
    return '',404

# sets up nginx for proxying 

@app.cli.command()
@click.option('--sites-available-directory', default='/etc/nginx/sites-available')
@click.option('--sites-enabled-directory', default='/etc/nginx/sites-enabled')
@click.option('--root-path', default="/home/pi/rpi-doorbot")
@click.option('--server-name', default='_')
def setup_nginx(sites_available_directory, sites_enabled_directory, server_name, root_path):
    (head,tail) = os.path.split(os.path.dirname(os.path.abspath(sys.argv[0])))
    if tail == '': #trailing slash
        head,_ = os.path.split(head)
    root_path,_ = os.path.split(head)
    site = 'doorbot.conf'
    conf_file_path = os.path.abspath(os.path.join(sites_available_directory, site))
    link_file_path = os.path.join(sites_enabled_directory, site)
    default_site_path = os.path.join(sites_enabled_directory, 'default')
    with open(conf_file_path, mode='w') as conf_file:
        conf_file.write(service_templates.NGINX_CONF.format(server_name=server_name, root_directory=root_path))
    try:
        os.symlink(conf_file_path, link_file_path)
    except IOError as e:
        if e.errno != errno.EEXIST:
            pass
    try:
        os.unlink(default_site_path)
    except IOError as e:
        if e.errno != errno.ENOENT:
            pass
    subprocess.check_call(['nginx', '-t'])
    subprocess.check_call(['nginx', '-s', 'reload'])


# CREATE SERVICES

services = {
    "api":              [service_templates.API,script_templates.API], 
    "doorlock":         [service_templates.DOORLOCK,script_templates.DOORLOCK],
    "doorswitch":       [service_templates.DOORSWITCH, script_templates.DOORSWITCH],
    "reset":            [service_templates.RESET,script_templates.RESET],
    "updateidcache" :   [service_templates.UPDATEIDCACHE, script_templates.UPDATEIDCACHE],
    "reader":           [service_templates.READER, script_templates.READER,],
}

@app.cli.command()
@click.option('--systemd-directory', default='/etc/systemd/system')
@click.option('--script-directory',  default='/usr/local/bin')
@click.option('--effective-user', default='pi')
def install_services(systemd_directory, script_directory, effective_user):
    (head,tail) = os.path.split(os.path.dirname(os.path.abspath(sys.argv[0])))
    if tail == '': #trailing slash
        head,_ = os.path.split(head)
    bin_path,_ = os.path.split(head)
   
    for name, templates in services.items():
        script_path = os.path.abspath(os.path.join(script_directory, '{}.sh'.format(name)))
        with open(script_path, mode='w') as unit_file:
            unit_file.write(templates[1].format(base=bin_path, user=effective_user))
        uid = getpwnam(effective_user).pw_uid
        gid =  getpwnam(effective_user).pw_gid
        os.chmod(script_path, 0o755)
        os.chown(script_path,uid, gid)

    for name, templates in services.items():
        unit_file_path = os.path.abspath(os.path.join(systemd_directory, 'doorbot-{}.service'.format(name)))
        script_path = os.path.abspath(os.path.join(script_directory, '{}.sh'.format(name)))
        with open(unit_file_path, mode='w') as unit_file:
            unit_file.write(templates[0].format(base=bin_path,script_path=script_path, user=effective_user))

    subprocess.check_call(['systemctl', 'daemon-reload'])
    for name in services:
        service = f"doorbot-{name}"
        subprocess.check_call(['systemctl', 'start', service])
        subprocess.check_call(['systemctl', 'enable', service])

@app.cli.command()
@click.option('-d', '--disable', default='False')
def stop_processes(disable):
    for name in services:
        service = f"doorbot-{name}"
        subprocess.check_call(['systemctl', 'stop', service])
        if disable:
            subprocess.check_call(['systemctl', 'enable', service])
    






if __name__== '__main__':
    app.run(debug=True) #use with vscode
