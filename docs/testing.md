# Testing And Validation

Formal Home Assistant unit tests are not included in this first pass.

Validation performed locally:

- Python syntax compilation for all integration modules.
- Manual review against the Task 2 requirements.
- Payload schema exercised through documented `mosquitto_pub` examples.

Recommended Home Assistant validation:

1. Install the integration manually.
2. Configure the built-in MQTT integration.
3. Add `Qingping MQTT Sensor` through the UI.
4. Use MQTT Explorer to publish `online` to the availability topic.
5. Use MQTT Explorer to publish the sample JSON state payload.
6. Confirm entities appear under a single Home Assistant device.
7. Publish updated state values and confirm live updates.
8. Publish `offline` and confirm entities become unavailable.
9. Reload the config entry and confirm MQTT subscriptions continue.
10. Remove the config entry and confirm subscriptions are cleaned up.

## MQTT Explorer Test Steps

Connect MQTT Explorer to the same broker configured in Home Assistant.

For a config entry using:

| Field | Value |
| --- | --- |
| Base topic | `qingping` |
| Device ID | `qp_air_001` |

publish:

```text
Topic: qingping/qp_air_001/availability
Payload: online
```

then publish:

```text
Topic: qingping/qp_air_001/state
```

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

Expected entities:

- Temperature
- Humidity
- Battery
- PM2.5
- CO2
- TVOC
- Illuminance
- Occupancy
- Low battery
- Signal strength
- Firmware
- Last seen

Publish changed values to the same state topic to confirm live updates. Publish `offline` to the availability topic to confirm entities become unavailable.

Recommended future test coverage:

- config flow success and duplicate-device handling
- valid JSON payload updates
- invalid JSON ignored without crashing
- dynamic entity creation for observed keys
- unload cleanup
- binary sensor boolean coercion
