"""
send start message to all daemons
"""
import redis

def startupDoorbot():
    daemons = ['doorbot_lock', 'doorbot_reader', 'doorbot_reset', 'doorbot_switch']


