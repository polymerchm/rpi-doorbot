"""
impliments a get that decodes byte strings automatically 
"""
import redis

r = redis.Redis()

def redisGet(key: str, default: any = None) -> any:
    value = r.get(key)
    if value == None:
        return default
    
    if isinstance(value, bytes):
        value = value.decode("utf-8")

    return value