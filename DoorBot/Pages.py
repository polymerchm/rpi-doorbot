from flask_stache import render_template
import flask
from urllib.parse import urlparse
from datetime import datetime
import Config

DEBUG = Config.get('DEBUG')


def get_env():
    request = flask.request
    host_url = urlparse( request.base_url ) 
    hostname = host_url.hostname
    env = "personal"
    if "rfid-dev" in hostname:
        env = "dev"
    elif "rfid-stage" in hostname:
        env = "stage"
    elif "rfid-prod" in hostname:
        env = "prod"
    return env

def render_tmpl( name, **context ):
    context[ 'env' ] = env = get_env()
    context[ 'is_lower_env' ] = True if env != "prod" else False

    print( f'Env: {context["env"]}' )
    print( f'Is lower: {context["is_lower_env"]}' )

    return render_template(
        name,
        **context,
    )