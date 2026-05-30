# Example MQTT Payloads

These payloads can be published with MQTT Explorer or `mosquitto_pub`.

When using MQTT Explorer:

1. Connect to the same broker configured in Home Assistant.
2. Create/select the topic shown below.
3. Paste the payload into the value editor.
4. Publish the message.
5. Enable retain for demo/testing if you want Home Assistant to receive the latest value after restart.

## Availability

```bash
mosquitto_pub -h 127.0.0.1 -t qingping/qp_air_001/availability -m online
```

```bash
mosquitto_pub -h 127.0.0.1 -t qingping/qp_air_001/availability -m offline
```

## Full Air Quality Payload

```bash
mosquitto_pub -h 127.0.0.1 -t qingping/qp_air_001/state -m '{"temperature":23.4,"humidity":48,"battery":86,"pm25":6,"co2":612,"tvoc":180,"illuminance":120,"occupancy":true,"low_battery":false,"rssi":-64,"firmware":"1.2.3","last_seen":"2026-05-27T10:15:00+00:00"}'
```

## Temperature/Humidity Device Payload

```bash
mosquitto_pub -h 127.0.0.1 -t qingping/qp_temp_001/state -m '{"temperature":22.1,"humidity":51,"battery":92,"rssi":-70,"firmware":"1.0.8","last_seen":"2026-05-27T10:20:00+00:00"}'
```

## Occupancy Device Payload

```bash
mosquitto_pub -h 127.0.0.1 -t qingping/qp_motion_001/state -m '{"motion":true,"occupancy":true,"illuminance":84,"battery":74,"rssi":-66,"firmware":"2.1.0","last_seen":"2026-05-27T10:22:00+00:00"}'
```
