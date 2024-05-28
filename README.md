# Inital setup of Raspberry Pi Zero 2 W version of Bodgery Doorbot

## basic concepts

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
    
---
### Flask based api

- mimics esp32-doorbot api for calls to MMS to get user info
- mustache-based user interface w/ admin password
    for local control
---

### reader.py

- pigpio library for **ISR** (may need the pigpio daemon running)
- daemon that reads Weigand codes (dat0, dat1, trigger)
        trigger is the output of an XOR gate of Dat0 and Dat1
- daemon pushes last legal keycode to redis
    daemon toggles LED and buzzer


    

