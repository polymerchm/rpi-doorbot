from redis import Redis
import jsonpickle
import hw.wiegand as wiegand
import DoorBot.Config as Config
import pigpio
from hw.initializeRedis import initializeRedis
from ..DoorBot.constants import *
from time import sleep
import signal, sys, os

# Bodgery Raspberry Pi Zero 2 W Doorbot
# reader daemon

# author: polymerchm

RUN_LOOP_ACTIVE = False
DEBUG = os.environ.get("DEBUG", True)
redis_cli = Redis()

def signalHandler(sig, frame):
    stopReader()
    sys.exit(0)

def stopReader():
    """
    catch any interrupts and kill event loop
    """
    global RUN_LOOP_ACTIVE
    RUN_LOOP_ACTIVE = False

def callback(bits, value):  
        """
        receivevd data from the reader
        """
        if DEBUG:
            print(f"Weigand output: bits={bits}, value={value}")
        
        redis_cli.publish('doorbot', value)



def main():
    """
    main event loop
    """
    global RUN_LOOP_ACTIVE

    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)

    RUN_LOOP_ACTIVE = True
    
    
    # if empty, load up initialization values from config file

    if not redis_cli.get(REBOOT_TIME):
        initializeRedis()

    gpio = Config.get('gpio')
    timing = Config.get('timing')
    pi = pigpio.pi()
   
    w = wiegand(pi, gpio['data0'], gpio['data1'], callback, timing['timeout'])

    while RUN_LOOP_ACTIVE:
        sleep(1)

    w.cancel()
    pi.stop()

if __name__ == "__main__":
    if DEBUG:
        main()
    else:
        print("should be run via systemctl service")








