from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_POSTCODE

class AmberConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Optionally, validate postcode here
            return self.async_create_entry(title=f"Amber ({user_input[CONF_POSTCODE]})", data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_POSTCODE): str,
        })
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return AmberOptionsFlowHandler(config_entry)

class AmberOptionsFlowHandler(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema({
            vol.Optional("scan_interval", default=self.config_entry.options.get("scan_interval", 300)): int,
        })
        return self.async_show_form(step_id="init", data_schema=data_schema, errors=errors)
