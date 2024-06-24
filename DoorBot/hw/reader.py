from redis import Redis
import jsonpickle
import requests, json
from requests.auth import HTTPDigestAuth
from urllib.parse import urljoin, urlencode, urlparse, urlunparse
from DoorBot.constants import *
import DoorBot.hw.wiegand as wiegand
import DoorBot.Config as Config
import DoorBot.hw.doorLock
from DoorBot.hw.initializeRedis import initializeRedis
import pigpio



from time import sleep
import signal, sys, os
import jsonpickle

# Bodgery Raspberry Pi Zero 2 W Doorbot
# reader daemon

# author: polymerchm

DEBUG = Config.get('DEBUG')
redis_cli = Redis()
pubsub = redis_cli.pubsub()
pubsub.subscribe('reader')

server = Config.get('server')
base_url = server['base_url']
user = server['user']
password = server['password']
dump_keys_request = "secure/dump_active_tags"
check_key_request = "entry/{}"

def signalHandler(sig, frame):
    redis_cli.publish(READER, 'stop')

def callback(bits, value):  
        """
        receivevd data from the reader
        """
        if DEBUG:
            print(f"Weigand output: bits={bits}, value={value}, id={(value & 0x1ffffff) >> 1}")
        redis_cli.publish(READER, jsonpickle.encode({'bits': bits, 'value': value}))

def rebuild_id_cache():
    pass

def main():
    """
    main event loop
    """
 

    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)


    # if empty, load up initialization values from config file

    if not redis_cli.get(REBOOT_TIME):
        initializeRedis()

    gpio = Config.get('gpio')
    timing = Config.get('timing')
    pi = pigpio.pi()
   
    w = wiegand.decoder(pi, gpio['data0'], gpio['data1'], callback, timing['timeout'])

    for message in pubsub.listen():
        if DEBUG:
            print(message)
        message_type = message['type']
        if message_type == 'subscribe':
            continue
        elif message_type == 'message':
            data = message['data'].decode("utf-8")
            if data == 'stop': # stop the daemmon
                 break
            else:
                data = jsonpickle.decode['data']
                token = data['value'] # raw 26 bit Wiegand code
                token &= 0x1ffffff # strip off upper parrity bit
                token >>= 1 # shift off lower parity bit to generate 24 bit id
                id = f"{token:010}"  # string padded out to 10 places with leading zeros
                
                position = redis_cli.lpos(FOB_LIST, id)
                if position != None:
                    # not in the local list,  go out to the server
                    server = Config.get('memserverberpress')
                    user = server['user']
                    password = server['password']
                    base_url = server['base_url']
                    url = base_url + check_key_request.format(id)
                    result = requests.get(url, auth=HTTPDigestAuth(user, password), verify=True)
                    
                    # ask the mss database about this id
                    # if valid:
                    #    if DEBUG:
                    #       print("adding FOB id {id} to list and opening the door")
                    #    redis_cli.lpush(FOB_LIST, id)
                    #    redis_cli.publish(DOOR_LOCK, "open")
                    pass
                else:
                    if DEBUG:
                        print("Opening Door for ID {id}")
                        redis_cli.publish(DOOR_LOCK, "open")


    w.cancel()
    pi.stop()

if __name__ == "__main__":
    if DEBUG:
        main()
    else:
        print("should be run via systemctl service")








