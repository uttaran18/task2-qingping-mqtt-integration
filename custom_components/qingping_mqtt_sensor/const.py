"""Constants for the Qingping MQTT Sensor integration."""

from __future__ import annotations

DOMAIN = "qingping_mqtt_sensor"

CONF_BASE_TOPIC = "base_topic"
CONF_DEVICE_ID = "device_id"
CONF_MODEL = "model"

DEFAULT_BASE_TOPIC = "qingping"
DEFAULT_MODEL = "Qingping Air Quality"
DEFAULT_NAME = "Qingping Sensor"

PLATFORMS = ["sensor", "binary_sensor"]

MANUFACTURER = "Qingping"

