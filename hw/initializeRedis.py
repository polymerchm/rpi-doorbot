from redis import Redis
from ..constants import  *
from lastreboot import lastreboot
from getserial import getserial

redis_cli = Redis()

redis_cli.set(REBOOT_TIME, lastreboot())
redis_cli.set(SERIAL_NUMBER, getserial())
