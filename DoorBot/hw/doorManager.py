import redis
import pigpio
from DoorBot.constants import *
import DoorBot.Config as Config
import redis
import sys, os, signal, time

timing = Config('timing')

DEBUG = True

def signalHandler(sig, frame):
    global RUN_LOOP_ACTIVE
    RUN_LOOP_ACTIVE = False

def main():

    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)

    redis = redis.Redis()
    redis.subscribe('doorbot')

    for message in redis.listen():
        print(message)

if __name__ == '__main__':
    if DEBUG:
        main()
    else:
        print("run as a daemon")








