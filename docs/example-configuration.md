# Example Configuration

The integration is configured through the Home Assistant UI. No YAML is required.

MQTT broker details are configured separately in Home Assistant's built-in MQTT integration:

```text
Settings -> Devices & services -> MQTT
```

This integration only needs the topic information for the Qingping device.

Example config flow values:

| Field | Value |
| --- | --- |
| Device name | Qingping Air Monitor |
| Device ID | qp_air_001 |
| Base MQTT topic | qingping |
| Model | Qingping Air Quality |

This creates subscriptions to:

```text
qingping/qp_air_001/state
qingping/qp_air_001/availability
```

The local bridge should publish retained MQTT state if immediate state restoration after Home Assistant restart is desired.
