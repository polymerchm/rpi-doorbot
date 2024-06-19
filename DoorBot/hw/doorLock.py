import redis
import pigpio
from DoorBot.constants import *
import DoorBot.Config as Config
import redis
import sys, os, signal, time
import threading

timing = Config.get('timing')
gpio = Config.get('gpio')
DEBUG = Config.get('DEBUG')
redis_cli = redis.Redis()
pubsub = redis_cli.pubsub()
pubsub.subscribe(DOOR_LOCK)


pi = pigpio.pi()
lock = gpio['lock']

pi.set_mode(lock, pigpio.OUTPUT)
pi.set_pull_up_down(lock, pigpio.PUD_DOWN)
pi.write(lock,pigpio.LOW)


def openDoor():
    if DEBUG:
        print("open lock request")
    redis_cli.set(DOOR_STATE, 'opened')
    pi.write(lock,pigpio.HIGH)
    

def closeDoor():
    if DEBUG:
        print("close lock request")
    redis_cli.set(DOOR_STATE, 'closed')
    pi.write(lock,pigpio.LOW)

def signalHandler(sig, frame):
    if DEBUG:
        print(f"stop requested via sigterm or sigint {sig}")
    redis_cli.publish(DOOR_LOCK,'stop')

def triggerDoorClose():
    if DEBUG:
        print("lock close triggered")
    redis_cli.publish(DOOR_LOCK, 'close')


def main():
    """
    use redis pubsub to react to lock state change request events.

    valid data:
        'open' - 
            if lock is not already open, open it and set state to open
        'close' -
            if lock is not already closed, close it and set state to closed
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
            lockState = redis_cli.get(DOOR_STATE)
            if data == 'open' and lockState != 'opened':
                # open the lock and start a timer to close it using threading
                openDoor()
                delay = float(timing['lockOpenTime'])
                if DEBUG:
                    print(f"Delay is {delay}")
                closer = threading.Timer(delay, triggerDoorClose)
                closer.start()
            elif data == 'close' and lockState != 'closed':
                closeDoor()
            elif data == 'stop':
                break
            else:
                print("invalid message data")


    print("lockLock daemon stopping")  
    closeDoor()
    redis_cli.set(DOOR_STATE, 'closed')
    #pi.stop() 


if __name__ == '__main__': 
    if DEBUG:
        print("starting lockLock daemon")
        main()
    else:
        print("run as a daemon")








