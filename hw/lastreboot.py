import psutil
import datetime

def get():
    value = psutil.boot_time()
    return datetime.datetime  \
        .fromtimestamp(value) \
        .strftime("%Y-%m-%d %H:%M:%S")