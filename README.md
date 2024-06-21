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

### Pinout for HAT  

- Console TxD     GPIO15(8)
- Console RxD     GPIO16(10)
- Console GND     GND

- Weigand 1       GPIO10 (19)
- Weigand 2       GPIO09 (21)
- Reader GND      GND
- Reader LED      GPIO17 (11)
- Reader Buzzer   GPIO18 (12)
- Reader format   GPIO23 (16)
- Door (relay)    GPIO22 (15)
- reset button    GPIO03 (5)
- door switch     GPIO24 (18)



### Non-data external connections
- door_switch_in, door_switch out (GND and pulled up data)
- +12V
- latch_in/latchout
- console (3 pin header)

API endpoints

    .../check_tag/<tag>             check tag against the server
    .../secure/dump_active_tags     get a json of all active tags 
                                (id is the key, validty is a bool)

    

