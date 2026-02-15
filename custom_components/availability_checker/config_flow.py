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
        self.config_entry = config_entry
        self._devices = list(config_entry.options.get(CONF_DEVICES, []))

    async def async_step_init(self, user_input: dict | None = None):
        return await self.async_step_manage()

    async def async_step_manage(self, user_input: dict | None = None):
        schema = vol.Schema({
            vol.Optional("name"): str,
            vol.Optional("host"): str,
        })

        if user_input is not None:
            name = user_input.get("name")
            host = user_input.get("host")
            if name and host:
                self._devices.append({"name": name, "host": host})
                return await self._show_manage()
            return await self._finish()

        return await self._show_manage()

    async def _show_manage(self):
        description = {"devices": self._devices}
        return self.async_show_form(step_id="manage", data_schema=vol.Schema({
            vol.Optional("name", default=""): str,
            vol.Optional("host", default=""): str,
        }), description_placeholders={"devices": str(self._devices)})

    async def _finish(self):
        return self.async_create_entry(title="devices", data={CONF_DEVICES: self._devices})
