# Architecture Explanation

## Communication Approach

This integration uses local MQTT as the communication boundary. The Qingping device is not contacted directly by Home Assistant. Instead, a local bridge publishes normalized JSON payloads to an MQTT broker.

This approach was selected because it is:

- local-first and privacy-preserving
- push-based, reducing Home Assistant polling load
- easy to test with deterministic sample payloads
- decoupled from the physical communication method used by the bridge
- resilient to future bridge changes as long as the MQTT schema remains stable

The main trade-off is that this integration depends on a separate bridge process. That bridge must handle BLE, local network, packet analysis, or vendor API communication. In production, the bridge would need its own monitoring and restart strategy.

## Data Flow

```text
Qingping device
  -> local bridge
  -> MQTT topic qingping/<device_id>/state
  -> Qingping MQTT Sensor runtime
  -> Home Assistant sensor and binary_sensor entities
```

Availability flows separately:

```text
qingping/<device_id>/availability
```

## State Model

The runtime object stores:

- latest JSON state payload
- latest availability state
- MQTT unsubscribe callbacks
- entity listeners

Sensor entities read from the latest in-memory payload. Entity properties do not perform I/O.

## Entity Hygiene

The integration uses:

- stable unique IDs: `<device_id>_<metric>`
- one Home Assistant device record per configured Qingping device
- manufacturer: `Qingping`
- configured model
- firmware version from the payload where available
- proper device class, state class, and native unit for supported metrics

Diagnostic entities:

- RSSI
- Last seen
- Firmware
- Low battery

## Lifecycle

The integration supports the standard Home Assistant config-entry lifecycle:

- UI config flow
- persistent config entry across restarts
- `async_setup_entry`
- `async_unload_entry`
- `async_reload_entry`
- platform forwarding for `sensor` and `binary_sensor`
- MQTT unsubscribe cleanup on unload

Entities are dynamically added when their keys first appear in a payload. This avoids creating unsupported entities for metrics the selected device does not genuinely report.

Reload is implemented as unload followed by setup. This confirms MQTT subscriptions are cleaned up and recreated without requiring a full Home Assistant restart.

## Entity Notes

The `tvoc` sensor intentionally does not set a `device_class`. Home Assistant does not currently expose a stable standard `SensorDeviceClass` for TVOC in this implementation target. The entity still sets `state_class` and native unit (`ppb`) so it behaves as a numeric measurement.

## Reliability Strategy

The integration:

- ignores invalid JSON without crashing
- marks entities unavailable when the availability topic reports offline
- keeps the latest valid payload in memory
- relies on MQTT retained messages for immediate state after restart, if configured by the bridge
- avoids polling, reducing battery impact on the physical device

## Known Limitations

- No direct BLE implementation is included.
- No config options flow is included yet.
- No automatic discovery of devices is included.
- MQTT payload schema validation is intentionally minimal.
- Unit tests are not included in this first pass.

With more time, the next improvements would be:

- options flow for topic changes
- diagnostics download
- stricter payload validation
- test coverage using Home Assistant's MQTT test helpers
- bridge health entity
- MQTT discovery or device discovery support

## Validation Approach

Formal unit tests are not included in this submission. Correctness was validated manually using the following steps:

1. Copy `custom_components/qingping_mqtt_sensor` into a local Home Assistant config directory.
2. Restart Home Assistant and confirm the integration appears in the UI.
3. Configure Home Assistant's built-in MQTT integration.
4. Complete the config flow with device ID `qp_air_001`.
5. Publish availability: `online` to `qingping/qp_air_001/availability`.
6. Publish a full state payload to `qingping/qp_air_001/state`.
7. Confirm entities are created only for keys present in the payload.
8. Confirm sensor values, units, device classes, and the single device record.
9. Publish availability `offline` and confirm entities become unavailable.
10. Reload the integration from the UI and confirm entities update on the next payload without a full Home Assistant restart.
11. Remove the integration and confirm no MQTT subscription errors remain in the logs.

With more time, test coverage would use Home Assistant's MQTT test helpers to cover payload parsing, availability transitions, dynamic entity creation, and unload cleanup in isolation.
