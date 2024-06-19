"""
monitors the magnetic door switch and reports back to redis (or elsewhere) 
timestamped changes

switch is connected between 3.3v and ground. 
"""
import redis
import pigpio
from DoorBot.constants import *
import DoorBot.Config as Config
import redis
import sys, os, signal, time
from datetime import datetime
import jsonpickle


gpio = Config.get('gpio')
DEBUG = Config.get('DEBUG')
redis_cli = redis.Redis()
pubsub = redis_cli.pubsub()
pubsub.subscribe("doorswitch")

print("starting the program")

def signalHandler(sig, frame):
    redis_cli.publish('doorswitch', 'stop')


signal.signal(signal.SIGINT, signalHandler)
signal.signal(signal.SIGTERM, signalHandler)

class DoorSwitch:
    def __init__(self, pi, switchPin, callback):
        self.pi = pi
        self.switchPin = switchPin
        self.callback = callback

        self.pi.set_mode(self.switchPin, pigpio.INPUT)
        self.pi.set_pull_up_down(self.switchPin, pigpio.PUD_UP)

        self.cb_switch = self.pi.callback(self.switchPin, pigpio.EITHER_EDGE, self._cb)

    def _cb(self, gpio, level, tick):
        """
        triggered on a transition of the door switch 
        """
        if DEBUG:
            print("triggered - gpio {gpio}, level {level}")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        door_is = 'open' if level == 0 else 'closed'
        self.callback(timestamp, door_is)
        

    def cancel(self):
        self.pi.cancel()
        redis_cli.publish('doorswitch','stop')

def main():
    pi = pigpio.pi()
    switch = gpio['switch']

    def callback(timestamp, switchState):
        if DEBUG:
            print(f" in doowSwitch callback, timestamp: {timestamp}, state: {switchState}")
        redis_cli.publish('doorswitch', jsonpickle.encode({'timestamp': timestamp, 'doorstate': switchState}))


    lock = DoorSwitch(pi, switch, callback)

    if DEBUG:
        print("entering the for loop")
    for message in pubsub.listen():
        if DEBUG:
            print(f" the message is {message}")
        message_type = message['type']
        if message_type == 'subscribe':
            continue
        elif message_type == 'message':
            data = message['data'].decode("utf-8")
            if data == 'stop': # stop the daemmon
                 break
            else:
                lockdata = jsonpickle.decode(data)
                timestamp = lockdata['timestamp']
                state = lockdata['doorstate']
                if DEBUG:
                    print(f"Door Switch state={state}, timestamp={timestamp}")
                redis_cli.lpush(DOOR_SWITCH_LOG,jsonpickle.encode({'doorstate': state, 'timestamp': timestamp}))  

    # exit for loop
    print(f"exited the loop and fell through")
    pi.stop()
    #exit

if __name__ == '__main__':
    main()










