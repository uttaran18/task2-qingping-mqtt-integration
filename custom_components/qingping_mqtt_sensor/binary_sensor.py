"""Binary sensor platform for Qingping MQTT Sensor."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MANUFACTURER
from .runtime import QingpingMqttRuntime


@dataclass(frozen=True, kw_only=True)
class QingpingBinarySensorDescription(BinarySensorEntityDescription):
    """Describe a Qingping MQTT binary sensor."""

    value_fn: Callable[[dict[str, Any]], bool | None]


BINARY_SENSOR_DESCRIPTIONS: tuple[QingpingBinarySensorDescription, ...] = (
    QingpingBinarySensorDescription(
        key="motion",
        translation_key="motion",
        device_class=BinarySensorDeviceClass.MOTION,
        value_fn=lambda data: _bool_or_none(data.get("motion")),
    ),
    QingpingBinarySensorDescription(
        key="occupancy",
        translation_key="occupancy",
        device_class=BinarySensorDeviceClass.OCCUPANCY,
        value_fn=lambda data: _bool_or_none(data.get("occupancy")),
    ),
    QingpingBinarySensorDescription(
        key="low_battery",
        translation_key="low_battery",
        device_class=BinarySensorDeviceClass.BATTERY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: _bool_or_none(data.get("low_battery")),
    ),
)


def _bool_or_none(value: Any) -> bool | None:
    """Convert common payload values to bool."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "on", "yes", "detected", "occupied"}
    return bool(value)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Qingping MQTT binary sensor entities."""
    runtime: QingpingMqttRuntime = entry.runtime_data
    added: set[str] = set()

    @callback
    def add_available_entities() -> None:
        new_entities = [
            QingpingBinarySensor(runtime, description)
            for description in BINARY_SENSOR_DESCRIPTIONS
            if description.key in runtime.data and description.key not in added
        ]
        if not new_entities:
            return
        added.update(entity.entity_description.key for entity in new_entities)
        async_add_entities(new_entities)

    add_available_entities()
    entry.async_on_unload(runtime.async_add_listener(add_available_entities))


class QingpingBinarySensor(BinarySensorEntity):
    """Representation of a Qingping MQTT binary sensor entity."""

    entity_description: QingpingBinarySensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        runtime: QingpingMqttRuntime,
        description: QingpingBinarySensorDescription,
    ) -> None:
        """Initialize a Qingping MQTT binary sensor."""
        self.runtime = runtime
        self.entity_description = description
        self._attr_unique_id = f"{runtime.device_id}_{description.key}"

    async def async_added_to_hass(self) -> None:
        """Register for runtime updates."""
        self.async_on_remove(self.runtime.async_add_listener(self.async_write_ha_state))

    @property
    def device_info(self) -> DeviceInfo:
        """Return device registry information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.runtime.device_id)},
            manufacturer=MANUFACTURER,
            model=self.runtime.model,
            name=self.runtime.entry.data["name"],
            sw_version=str(self.runtime.data.get("firmware"))
            if self.runtime.data.get("firmware")
            else None,
        )

    @property
    def available(self) -> bool:
        """Return whether the device is available."""
        return self.runtime.available and self.entity_description.key in self.runtime.data

    @property
    def is_on(self) -> bool | None:
        """Return the latest binary sensor state."""
        return self.entity_description.value_fn(self.runtime.data)

