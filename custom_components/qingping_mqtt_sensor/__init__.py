"""Qingping MQTT Sensor integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry, ConfigEntryNotReady
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, PLATFORMS
from .runtime import QingpingMqttRuntime

LOGGER = logging.getLogger(__name__)

type QingpingConfigEntry = ConfigEntry[QingpingMqttRuntime]


async def async_setup_entry(hass: HomeAssistant, entry: QingpingConfigEntry) -> bool:
    """Set up Qingping MQTT Sensor from a config entry."""
    runtime = QingpingMqttRuntime(hass, entry)
    entry.runtime_data = runtime

    try:
        await runtime.async_start()
    except HomeAssistantError as err:
        raise ConfigEntryNotReady(
            "MQTT is not ready. Configure and connect Home Assistant's MQTT "
            "integration before loading Qingping MQTT Sensor."
        ) from err

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: QingpingConfigEntry) -> bool:
    """Unload a Qingping MQTT Sensor config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    await entry.runtime_data.async_unload()
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: QingpingConfigEntry) -> None:
    """Reload a Qingping MQTT Sensor config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
