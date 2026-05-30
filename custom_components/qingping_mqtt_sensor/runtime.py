"""Runtime MQTT data store for Qingping MQTT Sensor."""

from __future__ import annotations

from collections.abc import Callable
import json
import logging
from typing import Any

from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback

from .const import CONF_BASE_TOPIC, CONF_DEVICE_ID, CONF_MODEL, DEFAULT_BASE_TOPIC, DEFAULT_MODEL

LOGGER = logging.getLogger(__name__)


class QingpingMqttRuntime:
    """Keep the latest MQTT payload and notify entities when it changes."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the runtime store."""
        self.hass = hass
        self.entry = entry
        self.data: dict[str, Any] = {}
        self.available = False
        self._unsubscribers: list[CALLBACK_TYPE] = []
        self._listeners: set[Callable[[], None]] = set()

    @property
    def device_id(self) -> str:
        """Return the configured device identifier."""
        return self.entry.data[CONF_DEVICE_ID]

    @property
    def base_topic(self) -> str:
        """Return the normalized MQTT base topic."""
        return self.entry.data.get(CONF_BASE_TOPIC, DEFAULT_BASE_TOPIC).strip("/")

    @property
    def state_topic(self) -> str:
        """Return the MQTT state topic."""
        return f"{self.base_topic}/{self.device_id}/state"

    @property
    def availability_topic(self) -> str:
        """Return the MQTT availability topic."""
        return f"{self.base_topic}/{self.device_id}/availability"

    @property
    def model(self) -> str:
        """Return the configured device model."""
        return self.entry.data.get(CONF_MODEL, DEFAULT_MODEL)

    async def async_start(self) -> None:
        """Subscribe to MQTT topics."""
        self._unsubscribers.append(
            await mqtt.async_subscribe(self.hass, self.state_topic, self._async_state_message)
        )
        self._unsubscribers.append(
            await mqtt.async_subscribe(
                self.hass, self.availability_topic, self._async_availability_message
            )
        )

    async def async_unload(self) -> None:
        """Unsubscribe from MQTT topics and clear listeners."""
        for unsubscribe in self._unsubscribers:
            unsubscribe()
        self._unsubscribers.clear()
        self._listeners.clear()

    @callback
    def async_add_listener(self, listener: Callable[[], None]) -> CALLBACK_TYPE:
        """Register a listener for MQTT data changes."""
        self._listeners.add(listener)

        def remove_listener() -> None:
            self._listeners.discard(listener)

        return remove_listener

    @callback
    def _notify_listeners(self) -> None:
        """Notify all registered listeners."""
        for listener in list(self._listeners):
            listener()

    @callback
    def _async_state_message(self, msg: mqtt.ReceiveMessage) -> None:
        """Handle an MQTT state payload."""
        try:
            payload = json.loads(msg.payload)
        except (TypeError, ValueError):
            LOGGER.warning("Ignoring invalid JSON payload on %s: %s", msg.topic, msg.payload)
            return

        if not isinstance(payload, dict):
            LOGGER.warning("Ignoring non-object JSON payload on %s: %s", msg.topic, msg.payload)
            return

        self.data = payload
        self.available = True
        self._notify_listeners()

    @callback
    def _async_availability_message(self, msg: mqtt.ReceiveMessage) -> None:
        """Handle an MQTT availability payload."""
        payload = str(msg.payload).strip().lower()
        self.available = payload in {"online", "true", "1", "available"}
        self._notify_listeners()

