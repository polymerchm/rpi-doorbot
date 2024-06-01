import DoorBot.Config as Config



# redis_tags = Config.get('redis')['redis_tags']

__all__ = [x for x in redis_tags]

REBOOT_TIME = 'reboot_time'
LAST_FOB_TIME = 'last_fob_time'
LAST_FOB_LIST_REFRESH = 'last_fob_list_refresh'
ROLE = 'role'
ROLE_OBJECT = 'role_object'
SERIAL_NUMBER = 'serial_number'
FOB_LIST = 'fob_list'
INVALID_FOB_LIST  = 'invalid_fob_list'
LAST_FOB = 'last_fob'

