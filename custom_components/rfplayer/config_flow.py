"""Config flow to configure the rfplayer integration."""
import os

import serial
import voluptuous as vol
import logging

from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_DEVICE, CONF_DEVICES
from homeassistant.core import callback
from homeassistant.helpers.selector import selector

from .const import *

log = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class RfplayerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a rfplayer config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Config flow started from UI."""
        errors = {}

        if user_input is not None:
            user_input[CONF_DEVICES] = {}

            user_input[CONF_DEVICE] = await self.hass.async_add_executor_job(
                get_serial_by_id, user_input[CONF_DEVICE]
            )

            if not errors:
                return self.async_create_entry(
                    title=user_input[CONF_DEVICE], data=user_input
                )

        ports = await self.hass.async_add_executor_job(serial.tools.list_ports.comports)
        list_of_ports = {}
        for port in ports:
            list_of_ports[
                port.device
            ] = f"{port}, s/n: {port.serial_number or 'n/a'}" + (
                f" - {port.manufacturer}" if port.manufacturer else ""
            )

        data = {
            vol.Required(CONF_DEVICE): vol.In(list_of_ports),
            vol.Required(CONF_AUTOMATIC_ADD, default=True): bool,
            vol.Required(CONF_FORMAT, default="JSON"): str,
            vol.Required(
                CONF_RECONNECT_INTERVAL, default=DEFAULT_RECONNECT_INTERVAL
            ): int,
            vol.Required(
                CONF_LEDACTIVITY, 
                default=True
            ): bool,
        }
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(data),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Define the config flow to handle options."""
        return RfPlayerOptionsFlowHandler(config_entry)


class RfPlayerOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a RFPLayer options flow."""

    def __init__(self, config_entry):
        """Initialize."""
        self.config_entry = config_entry

    # async def async_step_init(self, user_input: dict = None):
    #     """Manage the options."""
    #     log.debug("Init:%s",user_input)
 
    #     data = self.config_entry.data.copy()
    #     data[CONF_AUTOMATIC_ADD] = True
    #     data[CONF_FORMAT] = "JSON"
    #     data[CONF_FREQ_H] = 868350
    #     data[CONF_FREQ_L] = 433920
    #     data[CONF_SELECTIVITY_H] = 0
    #     data[CONF_SELECTIVITY_L] = 0
    #     data[CONF_SENSITIVITY_H] = 4
    #     data[CONF_SENSITIVITY_L] = 4
    #     data[CONF_DSPTRIGGER_H] = 6
    #     data[CONF_DSPTRIGGER_L] = 8
    #     data[CONF_RFLINK] = 1
    #     data[CONF_RFLINKTRIGGER_H] = 10
    #     data[CONF_RFLINKTRIGGER_L] = 12
    #     data[CONF_LBT] = 16
    #     data[CONF_LEDACTIVITY] = 1
    #     data[CONF_RECEIVER_DISABLE] = ""
    #     data[CONF_REPEATER_DISABLE] = ""
    #     data[CONF_TRACE] = ""
    #     return self.async_create_entry(title=data[CONF_DEVICE], data=data)

    async def async_step_init(self, user_input: dict = None):
        """Manage the options."""
        log.debug("Init:%s",user_input)
        if user_input is None:
            config = self.config_entry.data
            options = self.config_entry.options
            Init_Schema={
                        
                        vol.Required(
                            CONF_AUTOMATIC_ADD,
                            default=options.get(CONF_AUTOMATIC_ADD, config.get(CONF_AUTOMATIC_ADD,True))
                        ): bool,
                        vol.Required(
                            CONF_FORMAT, 
                            default=options.get(CONF_FORMAT, config.get(CONF_FORMAT,"JSON"))
                        ): vol.In(["OFF", "BINARY", "HEXA", "HEXA_FIXED","TEXT","XML","JSON"]),
                        vol.Required(
                            CONF_FREQ_H, 
                            default=options.get(CONF_FREQ_H, config.get(CONF_FREQ_H,868350))
                        ): vol.In(["0", "868950", "868350"]),
                        vol.Required(
                            CONF_FREQ_L, 
                            default=options.get(CONF_FREQ_L, config.get(CONF_FREQ_L,433920))
                        ): vol.In(["0", "433420", "433920"]),
                        vol.Required(
                            CONF_SELECTIVITY_H, 
                            default=options.get(CONF_SELECTIVITY_H, config.get(CONF_SELECTIVITY_H,0))
                        ): vol.In(["0", "1", "2", "3", "4", "5"]),
                        vol.Required(
                            CONF_SELECTIVITY_L, 
                            default=options.get(CONF_SELECTIVITY_L, config.get(CONF_SELECTIVITY_L,0))
                        ): vol.In(["0", "1", "2", "3", "4", "5"]),
                        vol.Required(
                            CONF_SENSITIVITY_H, 
                            default=options.get(CONF_SENSITIVITY_H, config.get(CONF_SENSITIVITY_H,4))
                        ): vol.In(["0", "1", "2", "3", "4", "5"]),
                        vol.Required(
                            CONF_SENSITIVITY_L, 
                            default=options.get(CONF_SENSITIVITY_L, config.get(CONF_SENSITIVITY_L,4))
                        ): vol.In(["0", "1", "2", "3", "4", "5"]),
                        vol.Required(
                            CONF_DSPTRIGGER_H, 
                            default=options.get(CONF_DSPTRIGGER_H, config.get(CONF_DSPTRIGGER_H,6))
                        ): int,
                        vol.Required(
                            CONF_DSPTRIGGER_L, 
                            default=options.get(CONF_DSPTRIGGER_L, config.get(CONF_DSPTRIGGER_L,8))
                        ): int,
                        vol.Required(
                            CONF_RFLINK, 
                            default=options.get(CONF_RFLINK, config.get(CONF_RFLINK,True))
                        ): bool,
                        vol.Required(
                            CONF_RFLINKTRIGGER_H, 
                            default=options.get(CONF_RFLINKTRIGGER_H, config.get(CONF_RFLINKTRIGGER_H,10))
                        ): int,
                        vol.Required(
                            CONF_RFLINKTRIGGER_L, 
                            default=options.get(CONF_RFLINKTRIGGER_L, config.get(CONF_RFLINKTRIGGER_L,12))
                        ): int,
                        vol.Required(
                            CONF_LBT, 
                            default=options.get(CONF_LBT, config.get(CONF_LBT,16))
                        ): int,
                        vol.Required(
                            CONF_LEDACTIVITY, 
                            default=options.get(CONF_LEDACTIVITY, config.get(CONF_LEDACTIVITY,True))
                        ): bool,
                        
                    }

            Init_Schema[CONF_RECEIVER_DISABLE] = selector({
                "select": {
                    "options": ["X10", "RTS", "VISONIC", "BLYSS", "CHACON", "OREGONV1", "OREGONV2", "OREGONV3/OWL", "DOMIA", "X2D", "KD101", "PARROT", "TIC", "FS20", "JAMMING", "EDISIO"],
                    "multiple":True
                },
            })
            Init_Schema[CONF_REPEATER_DISABLE] = selector({
                "select": {
                    "options": ["X10", "RTS", "VISONIC", "BLYSS", "CHACON", "OREGONV1", "OREGONV2", "OREGONV3/OWL", "DOMIA", "X2D", "KD101", "PARROT", "TIC", "FS20", "JAMMING", "EDISIO"],
                    "multiple":True
                },
            })
            Init_Schema[CONF_TRACE] = selector({
                "select": {
                    "options": ["ALARM", "RECEIVER", "TRANSMITTER", "TRANSCODER", "REPEATER", "JAMMING", "RFLINK"],
                    "multiple":True
                },
            })

            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema(Init_Schema),
            )

        else:
            data = self.config_entry.data.copy()
            data[CONF_AUTOMATIC_ADD] =True
            data[CONF_FORMAT] = "JSON"
            data[CONF_FREQ_H] = 868350
            data[CONF_FREQ_L] = 433920
            data[CONF_SELECTIVITY_H] = 0
            data[CONF_SELECTIVITY_L] = 0
            data[CONF_SENSITIVITY_H] = 4
            data[CONF_SENSITIVITY_L] = 4
            data[CONF_DSPTRIGGER_H] = 6
            data[CONF_DSPTRIGGER_L] = 8
            data[CONF_RFLINK] = True
            data[CONF_RFLINKTRIGGER_H] = 10
            data[CONF_RFLINKTRIGGER_L] = 12
            data[CONF_LBT] = 16
            data[CONF_LEDACTIVITY] = True
            data[CONF_RECEIVER_DISABLE] = ""
            data[CONF_REPEATER_DISABLE] = ""
            data[CONF_TRACE] = ""
            return self.async_create_entry(title=data[CONF_DEVICE], data=data)



class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


def get_serial_by_id(dev_path: str) -> str:
    """Return a /dev/serial/by-id match for given device if available."""
    by_id = "/dev/serial/by-id"
    if not os.path.isdir(by_id):
        return dev_path

    for path in (entry.path for entry in os.scandir(by_id) if entry.is_symlink()):
        if os.path.realpath(path) == dev_path:
            return path
    return dev_path
