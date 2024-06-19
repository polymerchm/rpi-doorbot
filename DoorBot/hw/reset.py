from  DoorBot.shutdownAll import shutdown
import os, time
import pigpio
import redis
import DoorBot.Config as Config

redis_cli = redis.Redis()
pubsub = redis_cli.pubsub()
pubsub.subscribe('reset')

DEBUG = Config.get('debug')

class Button:
    """
    define a button device

    callback is of the form
        callback(type: str)
            where type is either "short" or "long"
    """
    debouce_duration = 1000 # in microseconds
    long_hold_duration = 5 # seconds

    def _cb(self, pin, level, tick):
        if level == pigpio.TIMEOUT:
            self.pi.set_watchdog(self.pin, 0)
            redis_cli.publish('reset', 'do_reset')
        else:
            self.pi.set_watchdog(self.pin, self.long)
        
        

    def __init__(self, pi: pigpio.pi, pin: int, callback, long=0):
        self.pi = pi
        self.pin = pin
        self.callback = callback
        self.long = long if long != 0 else self.long_hold_duration
        self.pi.set_mode(self.pin, pigpio.INPUT)
        self.pi.set_pull_up_down(self.pin, pigpio.PUD_UP)
        self.pi.set_noise_filter(self.pin, self.debouce_duration)
        self.cb_button = self.pi.callback(self.pin, pigpio.EITHER_EDGE, self._cb)
        self.pi.set_watchdog(self.pin, self.long)
    
    def cancel(self):
        self.pi.close()

def resetDoorBot(button: Button):
    button.cancel()
    # reboot the doorbot
    time.sleep(5)
    if DEBUG:
        print("long press on reset occured")
    else:
        os.system('sudo shutdown -r now')
    
    

def main():

    pi = pigpio.pi()
    gpio = Config['gpio']

    button = Button(pi, gpio['reset'], shutdown)

    for message in pubsub.listen():
        if message['type'] == 'subscribe':
            continue
        elif message['type'] == 'message':
            data = message['date'].decode("utf-8")
            if data == 'stop':
                break
            elif data == 'do_reset':
                resetDoorBot(button)
    



        



