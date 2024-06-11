import redis
import pigpio
from DoorBot.constants import *
import DoorBot.Config as Config
import redis
import sys, os, signal, time
import threading

timing = Config.get('timing')
redis_cli = redis.Redis()
pubsub = redis_cli.pubsub()
pubsub.subscribe('doorbot')




DEBUG = True

def openDoor():
    if DEBUG:
        print("open door request")
    redis_cli.set(DOOR_STATE, 'opened')

def closeDoor():
    if DEBUG:
        print("close door request")
    redis_cli.set(DOOR_STATE, 'closed')

def signalHandler(sig, frame):
    if DEBUG:
        print(f"stop requested via sigterm or sigint {sig}")
    redis_cli.publish('doorbot','stop')

def triggerDoorClose():
    if DEBUG:
        print("door close triggered")
    redis_cli.publish('doorbot', 'close')


def main():
    """
    use redis pubsub to react to door state change request events.

    valid data:
        'open' - 
            if door is not already open, open it and set state to open
        'close' -
            if door is not already closed, close it and set state to closed
        'stop'
            terminate the daemon cleanly
    """

    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)

    for message in pubsub.listen():
        if DEBUG:
            print(message)
        if message['type'] == 'subscribe':
            continue
        elif message['type'] == 'message':
            data = message['data'].decode("utf-8")
            doorState = redis_cli.get(DOOR_STATE)
            if data == 'open' and doorState != 'opened':
                # open the door and start a timer to close it using threading
                openDoor()
                delay = float(timing['doorOpenTime'])
                print(f"Delay is {delay}")
                closer = threading.Timer(delay, triggerDoorClose)
                closer.start()
            elif data == 'close' and doorState != 'closed':
                closeDoor()
            elif data == 'stop':
                break
            else:
                print("invalid message data")


    print("doorManager daemon stopping")  
    closeDoor()
    redis_cli.set(DOOR_STATE, 'closed')
    #pi.stop() 


if __name__ == '__main__': 
    if DEBUG:
        print("starting doorManager daemon")
        main()
    else:
        print("run as a daemon")








