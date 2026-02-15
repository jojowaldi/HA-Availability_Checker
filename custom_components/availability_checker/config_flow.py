from __future__ import annotations

import voluptuous as vol
from typing import Any

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, CONF_DEVICES


class AvailabilityCheckerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is None:
            return self.async_show_form(step_id="user")

        return self.async_create_entry(title="Availability Checker", data={})

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self._config_entry = config_entry
        self._devices = list(config_entry.options.get(CONF_DEVICES, []))

    async def async_step_init(self, user_input: dict | None = None):
        """Manage options: add a device (name + host)."""
        schema = vol.Schema(
            {
                vol.Required("name"): str,
                vol.Required("host"): str,
            }
        )

        if user_input is None:
            return self.async_show_form(step_id="init", data_schema=schema)

        name = user_input["name"]
        host = user_input["host"]
        self._devices.append({"name": name, "host": host})
        return self.async_create_entry(title="devices", data={CONF_DEVICES: self._devices})
