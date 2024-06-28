"""
Clear out the redis database and populate key varariabled
"""
from redis import Redis
from DoorBot.constants import  *
from DoorBot.hw.lastreboot import lastreboot
from DoorBot.hw.getSerialNumber import getSerialNumber
import DoorBot.Config as Config

def initializeRedis(reinit=False):
    """
    rebuild the redis stores
    if serial number is already present, do not
    initialzed unless reinit is set to True
    """

    redis_cli = Redis()

    if redis_cli.get(SERIAL_NUMBER) == None or reinit: 
        redis_cli.flushall()
        redis_cli.set(REBOOT_TIME, lastreboot())
        redis_cli.set(SERIAL_NUMBER, getSerialNumber())
        location = Config.get('location')
        redis_cli.set(LOCATION, location)
        locations =  Config.get('valid_locations')
        for location in Config.get('valid_locations'):
            redis_cli.lpush(VALID_LOCATIONS, location)


if __name__ == '__main__':
    initializeRedis()
