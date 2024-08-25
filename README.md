# Inital setup of Raspberry Pi Zero 2 W version of Bodgery Doorbot

## basic concepts

A set of 7 daemons use redis pubsub.listen() in a 
for loop to wait for messages that represent incoming data.  

64-bit Raspian is needed for VSCode to work for remote editing/debugging

### redis for state management
- holds time of last reboot
- holds a list a valid keyfobs
- hold time of last fob list refresh
- holds serial number info for RPI
- holds id of last read successful fob
- hold time of last successful fob 
- redis pubsub capabilty used for interprocess communication   

---

## Daemons

### API.py

- Flask-based API also using SSE to update clients
- mimics esp32-doorbot api for calls to doorbot server to get user info
- mustache-based user interface w/ admin password
    for local control
- provides status and other info
---

### reader.py

- pigpio library for **ISR** (needs the pigpio daemon running)
- reads Weigand codes (dat0, dat1)
- trigger is falling edge on either dat0 or dat1
- daemon pushes last legal keycode to redis
- asks API to send sse message for UI update
    

### doorLock.py

- watches for door lock requests and enerizes/de-energizes the lock
    - updates the state of the lock in redis
    - asks API to send message for UI updates
    - uses threaded timer to relock the door after delay

### doorSwitch.py

- watches for changes in amagnetic reed switches
    - logs the changes and timestamp to redis
    - asks API to send messsage for UI update

### updateIDCache.py

- at designated interval, refreshed local ID tab list on redis

### reset.py

- after long press on reset button, reboot the reader
  - reset to "factory default" (not et implemented)
- after a short press, displays state of the doorbot 

### display.py

- maintains an i2C display
    - display is only active after a short touch on the reset button
    - on long touch, display a reset warning   

---


### initializeRedis.py

- set redis into its base state

### createServices.py

- write out the systemd service file base on the config file


---

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
- reset button    GPIO04 (7)
- door switch     GPIO24 (18)
- i2C SDA         GPIO02 (3)
- i2C SCL         GPIO03 (5)



### Non-data external connections
- door_switch_in, door_switch out (GND and pulled up data)
- +12V
- latch_in/latchout
- console (3 pin header)

### doorbot server endpoints used

    v1/check_tag/<tag>/<location>    check tag against the server 
    /secure/dump_active_tags         get a json of all active tags 
                                        (id is the key, validty is a bool)

### API endpoints

    /botStatus                          UI 
    /                                   UI
    /getStatus                          retreive lock and doot states
    /lock                               lock the door
    /unlock                             unlock the door
    /toggleLock                         toggle the lock
    /doorChange                         broadcast change in lock or 
                                        door status to clients via SSE

### Current Valid Locations are

  - cleanroom.door
  - garage.door
  - woodshop.door
  - dummy
  - front.door
  - back_main.door
  - back_annex.door

