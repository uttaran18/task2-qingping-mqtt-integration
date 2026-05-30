# Installation Instructions

## Manual Installation

1. Copy the integration folder:

```text
custom_components/qingping_mqtt_sensor
```

into the Home Assistant config directory:

```text
/config/custom_components/qingping_mqtt_sensor
```

2. Restart Home Assistant.
3. Configure the built-in MQTT integration:

```text
Settings -> Devices & services -> Add integration -> MQTT
```

Enter the broker/server address, port, username, and password there. The Qingping MQTT Sensor integration only subscribes to topics through Home Assistant's MQTT client; it does not manage broker credentials itself.

4. Add the integration from:

```text
Settings -> Devices & services -> Add integration -> Qingping MQTT Sensor
```

## Restart Points

Restart Home Assistant after:

- copying the integration manually
- installing or updating through HACS
- changing files under `custom_components/qingping_mqtt_sensor`

Config entry reload should work after the integration is installed.
