from homeassistant.core import HomeAssistant
from .const import DOMAIN, PLATFORMS


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def _async_reload_entry(hass: HomeAssistant, entry) -> None:
        await hass.config_entries.async_reload(entry.entry_id)

    entry.add_update_listener(_async_reload_entry)
    return True


async def async_unload_entry(hass: HomeAssistant, entry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
