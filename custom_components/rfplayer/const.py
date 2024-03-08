"""Constants for the rfplayer integration."""
DOMAIN = "rfplayer"
DATA_RFOBJECT = "rfobject"

CONF_AUTOMATIC_ADD =    "automatic_add"

CONF_FORMAT =           "conf_format"
CONF_RECEIVER_DISABLE = "conf_receiver_disable"
CONF_FREQ_H=            "conf_freq_h"
CONF_FREQ_L=            "conf_freq_l"
CONF_SELECTIVITY_H=     "conf_selectivity_h"
CONF_SELECTIVITY_L=     "conf_selectivity_l"
CONF_SENSITIVITY_H=     "conf_sensitivity_h"
CONF_SENSITIVITY_L=     "conf_sensitivity_l"
CONF_DSPTRIGGER_H=      "conf_dsptrigger_h"
CONF_DSPTRIGGER_L=      "conf_dsptrigger_l"
CONF_RFLINK=            "conf_rflink"
CONF_RFLINKTRIGGER_H=   "conf_rflinktrigger_h"
CONF_RFLINKTRIGGER_L=   "conf_rflinktrigger_l"
CONF_LBT=               "conf_lbt"
CONF_REPEATER_DISABLE=  "conf_repeater_disable"
CONF_LEDACTIVITY=       "conf_ledactivity"
CONF_TRACE=             "conf_trace"

LIST_CONF_COMMANDS=[
    {CONF_FORMAT:"FORMAT"},
    {CONF_RECEIVER_DISABLE:"RECEIVER"},
    {CONF_FREQ_H:"FREQ H"},
    {CONF_FREQ_L:"FREQ L"},
    {CONF_SELECTIVITY_H:"SELECTIVITY H"},
    {CONF_SELECTIVITY_L:"SELECTIVITY L"},
    {CONF_SENSITIVITY_H:"SENSITIVITY H"},
    {CONF_SENSITIVITY_L:"SENSITIVITY L"},
    {CONF_DSPTRIGGER_H:"DSPTRIGGER H"},
    {CONF_DSPTRIGGER_L:"DSPTRIGGER L"},
    {CONF_RFLINK:"RFLINK"},
    {CONF_RFLINKTRIGGER_H:"RFLINKTRIGGER H"},
    {CONF_RFLINKTRIGGER_L:"RFLINKTRIGGER L"},
    {CONF_LBT:"LBT"},
    {CONF_REPEATER_DISABLE:"REPEATER"},
    {CONF_LEDACTIVITY:"LEDACTIVITY"},
    {CONF_TRACE:"TRACE"},
]

CONF_RECONNECT_INTERVAL = "reconnect_interval"

DEFAULT_RECONNECT_INTERVAL = 10
DEFAULT_SIGNAL_REPETITIONS = 1

PLATFORMS = ["sensor", "switch", "number","cover"]

ATTR_EVENT = "event"

RFPLAYER_PROTOCOL = "rfplayer_protocol"

CONF_DEVICE_ADDRESS = "device_address"
CONF_FIRE_EVENT = "fire_event"
CONF_IGNORE_DEVICES = "ignore_devices"
CONF_SIGNAL_REPETITIONS = "signal_repetitions"
CONF_ENTITY_TYPE = "entity_type"
CONF_ENTITY_TODELETE = "entity_todelete"
CONF_ID = "id"
CONF_PLATFORM = "platform"

DATA_DEVICE_REGISTER = "device_register"
DATA_ENTITY_LOOKUP = "entity_lookup"

CONNECTION_TIMEOUT = 10

EVENT_BUTTON_PRESSED = "button_pressed"
EVENT_KEY_COMMAND = "command"
EVENT_KEY_ID = "id"
EVENT_KEY_SENSOR = "sensor"
EVENT_KEY_COVER = "cover"
EVENT_KEY_UNIT = "unit"
EVENT_KEY_PLATFORM = "platform"

RFPLAYER_GROUP_COMMANDS = ["allon", "alloff"]

SERVICE_SEND_COMMAND = "send_command"
SERVICE_SEND_RAW_COMMAND = "send_raw_command"
SERVICE_REMOVE_ENTITY = "remove_entity"
SERVICE_TEST_FRAME = "test_frame"

SIGNAL_AVAILABILITY = "rfplayer_device_available"
SIGNAL_HANDLE_EVENT = "rfplayer_handle_event_{}"
SIGNAL_EVENT = "rfplayer_event"

COMMAND_ON = "ON"
COMMAND_OFF = "OFF"
COMMAND_DIM = "DIM"
COMMAND_DOWN = "DOWN"
COMMAND_UP = "UP"
COMMAND_MY = "MY"

ENTITY_TYPE_SWITCH = "switch"
ENTITY_TYPE_COVER = "cover"
ENTITY_TYPE_SENSOR = "sensor"
ENTITY_TYPE_NUMBER = "number"

TEST_FRAME = "frame"
