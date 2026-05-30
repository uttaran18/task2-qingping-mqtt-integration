"""Config flow for Qingping MQTT Sensor."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_BASE_TOPIC,
    CONF_DEVICE_ID,
    CONF_MODEL,
    DEFAULT_BASE_TOPIC,
    DEFAULT_MODEL,
    DEFAULT_NAME,
    DOMAIN,
)


class QingpingMqttConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Qingping MQTT Sensor."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            device_id = user_input[CONF_DEVICE_ID].strip()
            base_topic = user_input[CONF_BASE_TOPIC].strip().strip("/")

            if not device_id:
                errors[CONF_DEVICE_ID] = "required"
            elif not base_topic:
                errors[CONF_BASE_TOPIC] = "required"
            elif not self.hass.services.has_service("mqtt", "publish"):
                errors["base"] = "mqtt_not_configured"
            else:
                await self.async_set_unique_id(device_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input.get("name") or DEFAULT_NAME,
                    data={
                        "name": user_input.get("name") or DEFAULT_NAME,
                        CONF_DEVICE_ID: device_id,
                        CONF_BASE_TOPIC: base_topic,
                        CONF_MODEL: user_input.get(CONF_MODEL) or DEFAULT_MODEL,
                    },
                )

        schema = vol.Schema(
            {
                vol.Required("name", default=DEFAULT_NAME): str,
                vol.Required(CONF_DEVICE_ID): str,
                vol.Required(CONF_BASE_TOPIC, default=DEFAULT_BASE_TOPIC): str,
                vol.Optional(CONF_MODEL, default=DEFAULT_MODEL): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
