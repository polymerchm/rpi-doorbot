"""
send stop message to all daemins (using the pubsub listen for loop protocol)
"""
import redis

channels = ["doorbot", "reader"]
r = redis.Redis()
for channel in channels:
    print(f"Sending shutdown via channel: {channel}")
    r.publish(channel, 'stop')
