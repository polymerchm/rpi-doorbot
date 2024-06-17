from redis import Redis
import jsonpickle
import hw.wiegand as wiegand
import DoorBot.Config as Config
import pigpio
from hw.initializeRedis import initializeRedis
from DoorBot.constants import *
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

def signalHandler(sig, frame):
    redis_cli.publish('reader', 'stop')

def callback(bits, value):  
        """
        receivevd data from the reader
        """
        if DEBUG:
            print(f"Weigand output: bits={bits}, value={value}")
        redis_cli.publish('reader', jsonpickle.encode({'bits': bits, 'value': value}))



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
   
    w = wiegand(pi, gpio['data0'], gpio['data1'], callback, timing['timeout'])

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
                bits = data['bits']
                token = data['value']

                #check against the list of valid tokens
                #if valid
                #redis_cli.publish(DOOR_LOCK, 'open')
                # if not there, chcek against the mms set


    w.cancel()
    pi.stop()

if __name__ == "__main__":
    if DEBUG:
        main()
    else:
        print("should be run via systemctl service")








