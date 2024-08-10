from  DoorBot.shutdownAll import shutDown
from DoorBot.constants import *
import os, time
import pigpio
import redis
import DoorBot.Config as Config
import signal

redis_cli = redis.Redis()
pubsub = redis_cli.pubsub()
pubsub.subscribe(RESET_BUTTON_CHANNEL)



DEBUG = Config.get('DEBUG')

def signalHandler(sig, frame):
    redis_cli.publish(RESET_BUTTON_CHANNEL, 'stop')


class Button:
    """
    define a button device

    callback is of the form
        callback(type: str)
            where type is either "short" or "long"
    """
    debouce_duration = 100 # in microseconds
    long_hold_duration = 2*1000 # seconds

    def __init__(self, pi: pigpio.pi, pin: int, callback, long=0):
        self.pi = pi
        self.pin = pin
        self.callback = callback
        self.long = long if long != 0 else self.long_hold_duration
        self.pi.set_mode(self.pin, pigpio.INPUT)
        self.pi.set_pull_up_down(self.pin, pigpio.PUD_UP)
        self.pi.set_glitch_filter(self.pin, self.debouce_duration)
        self.cb_button = self.pi.callback(self.pin, pigpio.EITHER_EDGE, self._cb)
    
    def _cb(self, pin, level, tick):
        if level == 0: # button tapped
            self.pi.set_watchdog(self.pin, self.long)
        elif level == 1: # button released before watchdog
            self.pi.set_watchdog(self.pin, 0)
            redis_cli.publish(RESET_BUTTON_CHANNEL, "display")
        elif level == pigpio.TIMEOUT: # long hold
            redis_cli.publish(RESET_BUTTON_CHANNEL, 'do_reset')
            self.pi.set_watchdog(self.pin, 0)
        
    
    def cancel(self):
        self.pi.stop()

def resetDoorBot(button: Button):
    button.cancel()
    # reboot the doorbot
    time.sleep(5)
    if DEBUG:
        print("long press on reset occured")
    else:
        os.system('sudo shutdown -r now')
    
def callback():
    print('in callback')

def main():

    pi = pigpio.pi()
    gpio = Config.get('gpio')

    button = Button(pi, gpio['reset_button'], callback)

    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)


    for message in pubsub.listen():
        if message['type'] == 'subscribe':
            continue
        elif message['type'] == 'message':
            data = message['data'].decode("utf-8")
            if data == 'stop':
                break
            elif data == 'do_reset':
                redis_cli.publish(DISPLAY_CHANNEL, "reset")
                resetDoorBot(button)
                break
            elif data == "display":
                redis_cli.publish(DISPLAY_CHANNEL, "display")

    # should never get here

if __name__ == '__main__':
    main()

    



        



