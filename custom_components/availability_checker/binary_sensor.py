from __future__ import annotations

import asyncio
import platform
from datetime import timedelta
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, CONF_DEVICES, DEFAULT_SCAN_INTERVAL


async def async_ping(host: str, timeout: float = 1.0) -> bool:
    system = platform.system().lower()
    if system == "windows":
        cmd = ["ping", "-n", "1", "-w", str(int(timeout * 1000)), host]
    else:
        cmd = ["ping", "-c", "1", "-W", str(int(timeout)), host]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await asyncio.wait_for(proc.communicate(), timeout + 2)
        return proc.returncode == 0
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except Exception:
            pass
        return False
    except Exception:
        return False


class PingCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, devices: list[dict[str, Any]], interval: int):
        LOGGER = logging.getLogger(__name__)
        super().__init__(
            hass,
            LOGGER,
            name="availability_checker",
            update_interval=timedelta(seconds=interval),
        )
        self.devices = devices

    async def _async_update_data(self) -> dict[str, bool]:
        tasks = [async_ping(d["host"]) for d in self.devices]
        try:
            results = await asyncio.gather(*tasks)
        except Exception as err:
            raise UpdateFailed(err)

        return {self.devices[i]["host"]: bool(results[i]) for i in range(len(self.devices))}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    devices = entry.options.get(CONF_DEVICES, [])
    interval = entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)

    if not devices:
        return True

    coordinator = PingCoordinator(hass, devices, interval)
    await coordinator.async_config_entry_first_refresh()

    entities = []
    for dev in devices:
        entities.append(PingBinarySensor(coordinator, entry, dev))

    async_add_entities(entities, True)
    return True


class PingBinarySensor(BinarySensorEntity):
    def __init__(self, coordinator: PingCoordinator, entry: ConfigEntry, device: dict[str, Any]):
        self.coordinator = coordinator
        self._entry = entry
        self._device = device
        self._attr_name = device.get("name")
        self._attr_unique_id = f"{entry.entry_id}_{device.get('host')}"
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.get(self._device.get("host"))

    async def async_update(self) -> None:
        await self.coordinator.async_request_refresh()
