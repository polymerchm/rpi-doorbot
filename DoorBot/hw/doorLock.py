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
lock = gpio['doorlock']

pi.set_mode(lock, pigpio.OUTPUT)
pi.set_pull_up_down(lock, pigpio.PUD_DOWN)
pi.write(lock,pigpio.LOW)


def unlockDoor():
    if DEBUG:
        print("open lock request")
    redis_cli.set(DOOR_STATE, 'unlocked')
    pi.write(lock,pigpio.HIGH)
    

def lockDoor():
    if DEBUG:
        print("close lock request")
    redis_cli.set(DOOR_STATE, 'locked')
    pi.write(lock,pigpio.LOW)

def signalHandler(sig, frame):
    if DEBUG:
        print(f"stop requested via sigterm or sigint {sig}")
    redis_cli.publish(DOOR_LOCK,'stop')

def triggerDoorClose():
    if DEBUG:
        print("lock close triggered")
    redis_cli.publish(DOOR_LOCK, 'lock')


def main():
    """
    use redis pubsub to react to lock state change request events.

    valid data:
        'unlock' - 
            if lock is not already unlocked, unlock it and set state to unlocked
        'lock' -
            if lock is not already locked, lock it and set state to locked
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
            if data == 'unlock' and lockState != 'unlocked':
                # open the lock and start a timer to close it using threading
                unlockDoor()
                delay = float(timing['lockOpenTime'])
                if DEBUG:
                    print(f"Delay is {delay}")
                relock = threading.Timer(delay, triggerDoorClose)
                relock.start()
            elif data == 'lock' and lockState != 'unlocked':
                lockDoor()
            elif data == 'stop':
                break
            else:
                print("invalid message data")


    print("Lock daemon stopping")  
    lockDoor()
    redis_cli.set(DOOR_STATE, 'locked')
    pi.stop() 


if __name__ == '__main__': 
    if DEBUG:
        print("starting lockLock daemon")
        main()
    else:
        print("run as a daemon")








