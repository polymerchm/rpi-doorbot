from redis import Redis
import hw.wiegand as wiegand
import DoorBot.Config as Config
import pigpio
from hw.initializeRedis import initializeRedis
from ..constants import *

# Bodgery Raspberry Pi Zero 2 W Doorbot
# reader daemon

# author: polymerchm


# redis_tags = Config.get('redis')['redis_tags']

# connect to Redis

redis_cli = Redis()

# if empty, load up initialization values from config file

if not redis_cli.get(REBOOT_TIME):
    initializeRedis()



gpio = Config.get('gpio')
pi = pigpio.pi()

def callback(bits, value):
    pass
    
w = wiegand(pi, gpio['data0'], gpio['data1'], gpio['timeout'])






