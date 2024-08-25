"""
send commands to the various daemons via redis


usage:

    doorbot_cli --<option>
    options:
        lock
        unlock
        stop_all
        restart
        reboot
"""

from redis import Redis
import argparse
from DoorBot.constants import *
from DoorBot.hw.getSerialNumber import getSerialNumber
from DoorBot.shutdownAll import shutDown
from DoorBot.redisGet import redisGet
from DoorBot.hw.reader import checkID
import sys


redis_cli = Redis()

def userName() -> str:

    lastFob = redisGet(LAST_FOB)
    result = checkID(lastFob, redisGet(LOCATION))
    if result.status_code != 200:
        print(f"invalid fob {lastFob} made it through the reader")
        sys.exit(1)
    return result.json()['full_name']


def fullStatus():
    """
    output full status of this doorbot
    """
    print(f"Doorbot serial number {getSerialNumber()}\nLocation {redisGet(LOCATION)}")
    print(f"Last reboot was {redisGet(REBOOT_TIME)}")
    print(f"Last refresh of ID cache was at {redisGet(LAST_FOB_LIST_REFRESH)}")
    print(f"Number of stored IDs is {redis_cli.llen(FOB_LIST)}")
    print(f"\nDoor State is {redisGet(DOOR_STATE)}")
    print(f"Door Lock is {redisGet(LOCK_STATE)}")
    print(f"Last FOB used was {redisGet(LAST_FOB)} at {redisGet(LAST_FOB_TIME)}")
    print(f"Member {userName()}")
    

def main():
    parser = argparse.ArgumentParser(
                    prog='doorbot_cli',
                    description='direct the daemons',
                    )
    parser.add_argument('--lock', action='store_true')
    parser.add_argument('--unlock', action='store_true')
    parser.add_argument('--stop_all', action='store_true')
    parser.add_argument('--restart',  action='store_true')
    parser.add_argument('--reboot', action='store_true')
    # configuration/botStatus
    parser.add_argument('--location',  action='store_true')
    parser.add_argument('--set_location', nargs='?', action='store', default=None)
    parser.add_argument('--cache_size',  action='store_true')
    parser.add_argument('--last_reboot',  action='store_true')
    parser.add_argument('--serial_number', action='store_true')
    parser.add_argument('--door_state',  action='store_true')
    parser.add_argument('--lock_state',  action='store_true')
    parser.add_argument('--status', action='store_true')
    parser.add_argument('--who', action='store_true')
    args = parser.parse_args()

    redis_cli = Redis()

    match vars(args):    
        #actions
        case {'lock':True}:
            redis_cli.publish(DOOR_LOCK_CHANNEL,'lock')
        case {'unlock':True}:
            redis_cli.publish(DOOR_LOCK_CHANNEL,'unlock')
        case {'stop_all':True}:
            shutDown()
        case {'restart':True}:
            pass
        case {'reboot':True}:
            pass
        case {'set_location':new_location} if new_location != None:
            # check new location in data base TODO
            old_location = redisGet(LOCATION)
            redis_cli.set(LOCATION, new_location)
            print(f"Location reset from {old_location} to {new_location}")
        #outputs
        case {'status':True}:
            fullStatus()
        case {'cache_size':True}:
            print(f"Number of stored IDs is {redis_cli.llen(FOB_LIST)}")
        case {'last_reboot':True}:
            print(f"Last reboot was {redisGet(REBOOT_TIME)}")
        case {'serial_number':True}:
            print(f"Doorbot serial number {getSerialNumber()}")
        case {'location':True}:
            print(f"Doorbot Location {redisGet(LOCATION)}")
        case {'door_state':True}:
            print(f"Door is {redisGet(DOOR_STATE)}")
        case {'lock_state':True}:
            print(f"Lock is {redisGet(LOCK_STATE)}")
        case {'who': True}:
            print(f"Member {userName()}")


if __name__ == '__main__':
    main()
