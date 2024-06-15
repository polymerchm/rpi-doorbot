# Inital setup of Raspberry Pi Zero 2 W version of Bodgery Doorbot

## basic concepts

The thee daemon, **reader**, **doorlock**, and **doorswitch** use redis pubsub.listen() in a 
for loop to wait for messages that represent incoming data.  

64-bit Raspian

### redis for state management
- holds time of last reboot
- holds a list a valid keyfobs
- hold time of last fob list refresh
- holds type of role
- holds role object info
- holds serial number info for RPI
- holds list of last valid keyfob codes
- holds list of most recent invalid keyfob codes
- hold value of read keycode and timestamp or ""
- hold the time of the last reboot
    
---
### Flask based api

- mimics esp32-doorbot api for calls to MMS to get user info
- mustache-based user interface w/ admin password
    for local control
- provides status and other info
---

### reader.py

- pigpio library for **ISR** (may need the pigpio daemon running)
- daemon that reads Weigand codes (dat0, dat1, trigger)
        trigger is the output of an XOR gate of Dat0 and Dat1
- daemon pushes last legal keycode to redis
    daemon toggles LED and buzzer

### doorLock.py

- watches for door lock requests and enerizes/de-energizes the lock
- updates the state of the lock in redis

### doorSwitch.py

- watches for changs in amagnetic reed switches
- logs the changes and timestamp to redis


    

