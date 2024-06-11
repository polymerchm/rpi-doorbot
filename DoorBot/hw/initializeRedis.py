from redis import Redis
from ..DoorBot.constants import  *
from lastreboot import lastreboot
from getserial import getserial

def initializeRedis():

    redis_cli = Redis()

    redis_cli.flushall()

    redis_cli.set(REBOOT_TIME, lastreboot())
    redis_cli.set(SERIAL_NUMBER, getserial())

if __name__ == '__main__':
    print('Initializing Redis')
    initializeRedis()
