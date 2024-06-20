"""
send stop message to all daemins (using the pubsub listen for loop protocol)
"""
import redis

def shutDown():
    channels = ["doorlock", "reader", "doorswitch", 'reset']
    daemons = ['doorbot_lock', 'doorbot_reader', 'doorbot_reset', 'doorbot_switch']
    r = redis.Redis()
    for channel in channels:
        print(f"Sending shutdown via channel: {channel}")
        r.publish(channel, 'stop')
    #in here kill all the daemons

if __name__ =='__main__':
    shutDown()

