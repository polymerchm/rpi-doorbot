# constants used throught rpi-doorbot

#redis keys
REBOOT_TIME = 'reboot_time'
LAST_FOB_TIME = 'last_fob_time'
LAST_FOB_LIST_REFRESH = 'last_fob_list_refresh'
ROLE = 'role'
ROLE_OBJECT = 'role_object'
SERIAL_NUMBER = 'serial_number'
FOB_LIST = 'fob_list'
INVALID_FOB_LIST  = 'invalid_fob_list'
LAST_FOB = 'last_fob'
DOOR_SWITCH_LOG = 'door_switch_log'
LOCATION = 'location'
VALID_LOCATIONS = 'valid_locations'

#door/lock current state

DOOR_STATE = 'door_state'
LOCK_STATE = 'lock_state'

#pubsib channels

CACHE_REBUILD_CHANNEL = 'cache_rebuild_channel'
RESET_BUTTON_CHANNEL = 'reset_button'
DOOR_LOCK_CHANNEL = 'door_lock_channel'
DOOR_SWITCH_CHANNEL = 'door_switch_channel'
READER_CHANNEL = 'reader_channel'
DISPLAY_CHANNEL = 'display_channel'

