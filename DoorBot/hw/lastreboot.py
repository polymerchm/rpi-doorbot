"""

return last reboot datetime as a string

"""
import psutil
import datetime

def lastreboot()->str:
    """
    return text version of last reboot
    """
    value = psutil.boot_time()
    return datetime.datetime  \
        .fromtimestamp(value) \
        .strftime("%Y-%m-%d %H:%M:%S")

if __name__ == '__main__':
    print(f"Last Reboot was {lastreboot()}")