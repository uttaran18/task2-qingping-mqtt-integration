# Qingping MQTT Sensor - Custom Home Assistant Integration

This repository contains a custom Home Assistant integration for a Qingping smart sensor using a local MQTT communication boundary.

Repository: https://github.com/uttaran18/task2-qingping-mqtt-integration

The implementation is intentionally scoped: it does not clone or reuse the community Qingping integration. It assumes a local bridge publishes Qingping readings to MQTT and focuses on Home Assistant integration lifecycle, entity modelling, reload/unload behaviour, and clean documentation.

## Scope

Supported communication path:

```text
Qingping sensor -> local bridge -> MQTT broker -> custom Home Assistant integration
```

The bridge may be BLE-based, local-network-based, or vendor-API-based. That bridge is outside this integration's scope. This integration consumes normalized local MQTT JSON payloads.

## MQTT Topics

Default base topic:

```text
qingping
```

For device ID `qp_air_001`, publish to:

```text
qingping/qp_air_001/state
qingping/qp_air_001/availability
```

Availability payloads:

```text
online
offline
```

Example state payload:

```json
{
  "temperature": 23.4,
  "humidity": 48,
  "battery": 86,
  "pm25": 6,
  "co2": 612,
  "tvoc": 180,
  "illuminance": 120,
  "motion": false,
  "occupancy": true,
  "low_battery": false,
  "rssi": -64,
  "firmware": "1.2.3",
  "last_seen": "2026-05-27T10:15:00+00:00"
}
```

Only keys present in the MQTT payload are created as entities.

## Installation

1. Ensure the built-in Home Assistant MQTT integration is configured and connected to a broker.
   - Go to `Settings -> Devices & services -> Add integration -> MQTT`.
   - Enter the broker host, port, username, and password there.
   - This custom integration does not store MQTT server credentials.
2. Copy this folder into Home Assistant:

```text
custom_components/qingping_mqtt_sensor
```

3. Restart Home Assistant.
4. Go to `Settings -> Devices & services -> Add integration`.
5. Search for `Qingping MQTT Sensor`.
6. Enter:
   - Device name: `Qingping Air Monitor`
   - Device ID: `qp_air_001`
   - Base MQTT topic: `qingping`
   - Model: `Qingping Air Quality`

If setup logs say MQTT is not ready or cannot subscribe to the topic, configure the built-in MQTT integration first, confirm it is connected, then reload this integration.

## Manual Test

You can test the integration with MQTT Explorer before building a real Qingping bridge.

Connect MQTT Explorer to the same broker configured in Home Assistant's built-in MQTT integration.

For this example config:

| Field | Value |
| --- | --- |
| Base topic | `qingping` |
| Device ID | `qp_air_001` |

Publish availability:

```bash
mosquitto_pub -h 127.0.0.1 -t qingping/qp_air_001/availability -m online
```

In MQTT Explorer, create or select this topic:

```text
qingping/qp_air_001/availability
```

Payload:

```text
online
```

Publish state:

```bash
mosquitto_pub -h 127.0.0.1 -t qingping/qp_air_001/state -m '{"temperature":23.4,"humidity":48,"battery":86,"pm25":6,"co2":612,"tvoc":180,"illuminance":120,"occupancy":true,"low_battery":false,"rssi":-64,"firmware":"1.2.3","last_seen":"2026-05-27T10:15:00+00:00"}'
```

In MQTT Explorer, create or select this topic:

```text
qingping/qp_air_001/state
```

Payload:

```json
{
  "temperature": 23.4,
  "humidity": 48,
  "battery": 86,
  "pm25": 6,
  "co2": 612,
  "tvoc": 180,
  "illuminance": 120,
  "occupancy": true,
  "low_battery": false,
  "rssi": -64,
  "firmware": "1.2.3",
  "last_seen": "2026-05-27T10:15:00+00:00"
}
```

Use retained messages during demos if you want Home Assistant to receive the latest state again after restart.

Expected result:

- One Home Assistant device is created.
- Sensor entities appear for the keys in the payload.
- Entity states update live when new MQTT payloads arrive.
- Entities become unavailable when availability is `offline`.

To test live updates in MQTT Explorer, publish the same state topic again with changed values:

```json
{
  "temperature": 24.1,
  "humidity": 52,
  "battery": 85,
  "pm25": 8,
  "co2": 650,
  "tvoc": 190,
  "illuminance": 95,
  "occupancy": false,
  "low_battery": false,
  "rssi": -67,
  "firmware": "1.2.3",
  "last_seen": "2026-05-27T10:20:00+00:00"
}
```

To test offline handling, publish:

```text
Topic: qingping/qp_air_001/availability
Payload: offline
```

## Dependencies

| Dependency | Version | Notes |
| --- | --- | --- |
| Home Assistant Core | v2026.5.4 | 
| MQTT integration | Built-in | Required. |
| MQTT broker | Any HA-compatible broker | Mosquitto recommended for local testing. |
| Python package requirements | None | No external Python dependencies. |

## Assumptions And Limitations

- A local MQTT publisher/bridge already exists.
- Direct BLE parsing is intentionally out of scope for this submission.
- Payload schema is normalized JSON.
- Entities are created only for fields observed in the payload.
- The integration treats MQTT as local push and does not poll the device.
- Unit conversion is delegated to Home Assistant where supported by `device_class`.

## AI Disclosure

AI assistance was used to draft and structure this assessment implementation.
