"""
send stop message to all daemins (using the pubsub listen for loop protocol)
"""
import redis
from DoorBot.constants import *

def shutDown():
    channels = [DOOR_LOCK_CHANNEL, 
                RESET_BUTTON_CHANNEL,
                DISPLAY_CHANNEL, 
                READER_CHANNEL,
                DOOR_SWITCH_CHANNEL, 
                CACHE_REBUILD_CHANNEL
                ]
    daemons = ['doorbot_lock', 'doorbot_reader', 'doorbot_reset', 'doorbot_switch']
    r = redis.Redis()
    for channel in channels:
        print(f"Sending shutdown via channel: {channel}")
        r.publish(channel, 'stop')
    #in here kill all the daemons

if __name__ =='__main__':
    shutDown()

