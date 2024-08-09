"""
manage the display on the Doorbot
"""


from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from luma.core.render import canvas
from PIL import Image, ImageDraw, ImageFont

import DoorBot.Config as Config
from DoorBot.constants import *
from DoorBot.hw.getIPAddress import getIPinfo
from DoorBot.hw.reader import checkID
from DoorBot.redisGet import redisGet
import redis
import signal, os, sys
import threading
from time import sleep
from pathlib import Path


redis_cli = redis.Redis()
pubsub = redis_cli.pubsub()
pubsub.subscribe(DISPLAY_CHANNEL)

display = Config.get('display')

WIDTH = display['width']
HEIGHT = display['height']
addr = display['address']
relativeLogoImagePath = display['image']
location = redisGet(LOCATION)
DEBUG = Config.get('DEBUG')


serial = i2c(port=1, address=addr)
device = sh1106(serial)
device.clear()

hostname, ipaddress = getIPinfo()

logoPath = Path(__file__).parents[1].joinpath(relativeLogoImagePath)
logoImage = Image.open(logoPath)
posn = ((device.width - logoImage.width) // 2, 0)

Font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",10)

def displayLogo():
    image = Image.new("1", device.size, "white") # set background
    image.paste(logoImage, posn)
    device.display(image)

def signalHandler(sig, frame):
    redis_cli.publish(DISPLAY_CHANNEL, 'stop')

def normal_display():
    delay = 2
    displayLogo()
    sleep(delay)
    # display the name and ip address
    device.clear()
    with canvas(device) as draw:
        draw.text((0,0), f"IP: \n   {ipaddress}",fill="white", font=Font)
        draw.text((0,25), f"Hostname: \n   {hostname}",fill="white", font=Font)
    sleep(delay)
    #display the cache size/refresh
    device.clear()
    with canvas(device) as draw:
        draw.text((0,0), f"CacheSize:\n  {redis_cli.llen(FOB_LIST)}",fill="white", font=Font)
        draw.text((0,25), f"Last Refresh:\n  {redisGet(LAST_FOB_LIST_REFRESH)}",fill="white", font=Font)
    sleep(delay)
    # last reboot
    device.clear()
    with canvas(device) as draw:
        draw.text((0,0), f"Last Reboot:\n  {redisGet(REBOOT_TIME)}",fill="white", font=Font)
    sleep(delay)
    #clear the display
    lastFob = redisGet(LAST_FOB)
    lastEntry = redisGet(LAST_FOB_TIME)
    result = checkID(lastFob, location)
    if result.status_code != 200:
        print("invalid fob made it through the reader")
        sys.exit(1)
    obj = result.json()
    with canvas(device) as draw:
        draw.text((0,0), f"Last Entry:\n {obj['full_name']}",fill="white", font=Font)
        draw.text((0,25), f"Time:\n  {lastEntry}" ,fill="white", font=Font)
    sleep(delay)
    device.clear()

def resetDisplay():
    resetFont = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",40)
    device.clear()
    with canvas(device) as draw:
        draw.text((5,0), f"Reset",fill="white", font=resetFont)
    sleep(3)
    device.clear()
        


def main():
    """
    main event loop
    """
 
    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)

    for message in pubsub.listen():
        if message['type'] == 'subscribe':
            continue
        elif message['type'] == 'message':
            data = message['data'].decode("utf-8")
            if data == 'stop':
                break
            elif data == 'display':
                normal_display() # display the data
            elif data == 'reset':
                resetDisplay() # display the reset   

if __name__ == '__main__':
    main()


