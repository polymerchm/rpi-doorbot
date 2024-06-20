from redis import Redis
from DoorBot.constants import  *
from DoorBot.hw.lastreboot import lastreboot
from DoorBot.hw.getSerialNumber import getSerialNumber
from DoorBot.Config import Config

def initializeRedis():

    redis_cli = Redis()

    redis_cli.flushall()

    redis_cli.set(REBOOT_TIME, lastreboot())
    redis_cli.set(SERIAL_NUMBER, getSerialNumber())
    redis_cli.set(LOCATION, Config.get('location'))

if __name__ == '__main__':
    print('Initializing Redis')
    initializeRedis()
