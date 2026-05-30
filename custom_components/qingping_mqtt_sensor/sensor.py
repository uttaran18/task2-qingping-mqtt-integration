"""Sensor platform for Qingping MQTT Sensor."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_MILLION,
    LIGHT_LUX,
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    EntityCategory,
    UnitOfTemperature,
)
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.dt import parse_datetime

from .const import DOMAIN, MANUFACTURER
from .runtime import QingpingMqttRuntime


def _parse_timestamp(value: Any) -> Any:
    """Parse an ISO timestamp payload for Home Assistant timestamp sensors."""
    if not value:
        return None
    if isinstance(value, str):
        return parse_datetime(value)
    return value


@dataclass(frozen=True, kw_only=True)
class QingpingSensorDescription(SensorEntityDescription):
    """Describe a Qingping MQTT sensor."""

    value_fn: Callable[[dict[str, Any]], Any]


SENSOR_DESCRIPTIONS: tuple[QingpingSensorDescription, ...] = (
    QingpingSensorDescription(
        key="temperature",
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data.get("temperature"),
    ),
    QingpingSensorDescription(
        key="humidity",
        translation_key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda data: data.get("humidity"),
    ),
    QingpingSensorDescription(
        key="battery",
        translation_key="battery",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda data: data.get("battery"),
    ),
    QingpingSensorDescription(
        key="illuminance",
        translation_key="illuminance",
        device_class=SensorDeviceClass.ILLUMINANCE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=LIGHT_LUX,
        value_fn=lambda data: data.get("illuminance"),
    ),
    QingpingSensorDescription(
        key="pm25",
        translation_key="pm25",
        device_class=SensorDeviceClass.PM25,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        value_fn=lambda data: data.get("pm25"),
    ),
    QingpingSensorDescription(
        key="co2",
        translation_key="co2",
        device_class=SensorDeviceClass.CO2,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        value_fn=lambda data: data.get("co2"),
    ),
    QingpingSensorDescription(
        key="tvoc",
        translation_key="tvoc",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="ppb",
        value_fn=lambda data: data.get("tvoc"),
    ),
    QingpingSensorDescription(
        key="rssi",
        translation_key="rssi",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("rssi"),
    ),
    QingpingSensorDescription(
        key="last_seen",
        translation_key="last_seen",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: _parse_timestamp(data.get("last_seen")),
    ),
    QingpingSensorDescription(
        key="firmware",
        translation_key="firmware",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("firmware"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Qingping MQTT sensor entities."""
    runtime: QingpingMqttRuntime = entry.runtime_data
    added: set[str] = set()

    @callback
    def add_available_entities() -> None:
        new_entities = [
            QingpingSensor(runtime, description)
            for description in SENSOR_DESCRIPTIONS
            if description.key in runtime.data and description.key not in added
        ]
        if not new_entities:
            return
        added.update(entity.entity_description.key for entity in new_entities)
        async_add_entities(new_entities)

    add_available_entities()
    entry.async_on_unload(runtime.async_add_listener(add_available_entities))


class QingpingSensor(SensorEntity):
    """Representation of a Qingping MQTT sensor entity."""

    entity_description: QingpingSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        runtime: QingpingMqttRuntime,
        description: QingpingSensorDescription,
    ) -> None:
        """Initialize a Qingping MQTT sensor."""
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
    def native_value(self) -> Any:
        """Return the latest sensor value."""
        return self.entity_description.value_fn(self.runtime.data)
