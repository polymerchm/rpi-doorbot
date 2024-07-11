import redis
import DoorBot.Config as Config
from DoorBot.constants import *
from threading import Timer
from datetime import datetime
import requests
import json
import signal
import sys

"""
at approriate intervals, update the ID cacahe in Redis 
A threaded timer performs the rebuild.add()
a signal via redis pubsub will stop the timer and end the process 
"""

redis_cli = redis.Redis()
pubsub = redis_cli.pubsub()
pubsub.subscribe(CACHE_REBUILD_CHANNEL)

server = Config.get('server')
user = server['user']
password = server['password']
base_url = server['base_url']
url = base_url + 'secure/dump_active_tags'

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

def rebuildCache():
    
    #get the current list from the server
    auth = (user, password)
    print(url)
    try:
        results = requests.get(url, auth=auth)
    except:
        print("requeat failed")
        sys.exit(1)
    if results.status_code != 200:
    # test that it is good, else print an error message to the log and return
        print("Could not retreive id object")
    else:
        id_obj = json.loads(results.text)
        #erase the previous list
        redis_cli.delete(FOB_LIST)
        #build the new list, using the value and the key
        for id,value in id_obj.items():
            if value:
                redis_cli.lpush(FOB_LIST,id)
            else:
                print(id,value)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        redis_cli.set(LAST_FOB_LIST_REFRESH, timestamp)


def signalHandler(sig, frame):
    redis_cli.publish(CACHE_REBUILD_CHANNEL,'stop')


def updateIDCache():
    """
    set up a event loop for timer based updates of the user id list in redis
    can be stopped by sigterm and sigint
    """
    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
    # initiate the timer thread here
    rebuild_cache_interval = Config.get('timing')['rebuildCacheInterval']
    timer = RepeatTimer(rebuild_cache_interval, rebuildCache)
    timer.start()

    #perform initial rebuild
    rebuildCache()

    for message in pubsub.listen():
        if message['type'] == 'subscribe':
            continue
        elif message['type'] == 'message':
            data = message['data'].decode("utf-8")
            if data == 'stop':
                break

    # fell through after a stop command        
    timer.cancel()


if __name__ == '__main__':
    updateIDCache()


