"""Config flow for Hoymiles."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from hoymiles_g3_modbus_tcp import Inverter, InverterConfig
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_CONNECTION_TYPE,
    CONF_FAST_INTERVAL,
    CONF_INCLUDE_DIAGNOSTICS,
    CONF_INCLUDE_GENERATOR,
    CONF_INCLUDE_SETTINGS,
    CONF_MAX_BLOCK,
    CONF_MAX_ENERGY_RATE,
    CONF_READ_RETRIES,
    CONF_SENSOR_PROFILE,
    CONF_SLOW_INTERVAL,
    CONF_TIMEOUT,
    CONF_UNIT,
    CONNECTION_DTS_ETHERNET,
    CONNECTION_MODBUS_GATEWAY,
    CONNECTION_TYPES,
    DEFAULT_FAST_INTERVAL,
    DEFAULT_MAX_BLOCK,
    DEFAULT_MAX_ENERGY_RATE,
    DEFAULT_PORT,
    DEFAULT_READ_RETRIES,
    DEFAULT_SLOW_INTERVAL,
    DEFAULT_TIMEOUT,
    DEFAULT_UNIT,
    DOMAIN,
    PROFILE_FULL,
    PROFILE_MINIMAL,
    PROFILE_STANDARD,
)

_LOGGER = logging.getLogger(__name__)


async def _validate_connection(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    config = InverterConfig(
        host=data[CONF_HOST],
        port=data[CONF_PORT],
        unit=data.get(CONF_UNIT, DEFAULT_UNIT),
        timeout=data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT),
    )
    inv = Inverter(config)
    await inv.connect()
    try:
        info = await inv.detect()
    finally:
        await inv.close()
    return {
        "title": f"Hoymiles {info.inverter_model}",
        "model": info.inverter_model,
    }


class HoymilesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hoymiles."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                meta = await _validate_connection(self.hass, user_input)
            except Exception as err:
                _LOGGER.debug("Connection failed: %s", err)
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(
                    f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}:{user_input.get(CONF_UNIT, 1)}"
                )
                self._abort_if_unique_id_configured()
                user_input.setdefault(CONF_SENSOR_PROFILE, PROFILE_STANDARD)
                user_input.setdefault(CONF_FAST_INTERVAL, DEFAULT_FAST_INTERVAL)
                user_input.setdefault(CONF_SLOW_INTERVAL, DEFAULT_SLOW_INTERVAL)
                return self.async_create_entry(title=meta["title"], data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_CONNECTION_TYPE, default=CONNECTION_DTS_ETHERNET): vol.In(
                    CONNECTION_TYPES
                ),
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=65535)
                ),
                vol.Required(CONF_UNIT, default=DEFAULT_UNIT): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=247)
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        return HoymilesOptionsFlowHandler(config_entry)


class HoymilesOptionsFlowHandler(config_entries.OptionsFlow):
    """Options for polling and entity exposure."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        entry = self.config_entry
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SENSOR_PROFILE,
                    default=entry.options.get(
                        CONF_SENSOR_PROFILE,
                        entry.data.get(CONF_SENSOR_PROFILE, PROFILE_STANDARD),
                    ),
                ): vol.In(
                    {
                        PROFILE_MINIMAL: "Minimal (PV, grid, power flows)",
                        PROFILE_STANDARD: "Standard (recommended)",
                        PROFILE_FULL: "Full (all readable registers)",
                    }
                ),
                vol.Required(
                    CONF_FAST_INTERVAL,
                    default=entry.options.get(
                        CONF_FAST_INTERVAL, entry.data.get(CONF_FAST_INTERVAL, DEFAULT_FAST_INTERVAL)
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=300)),
                vol.Required(
                    CONF_SLOW_INTERVAL,
                    default=entry.options.get(
                        CONF_SLOW_INTERVAL,
                        entry.data.get(CONF_SLOW_INTERVAL, DEFAULT_SLOW_INTERVAL),
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=900)),
                vol.Required(
                    CONF_INCLUDE_SETTINGS,
                    default=entry.options.get(
                        CONF_INCLUDE_SETTINGS, entry.data.get(CONF_INCLUDE_SETTINGS, False)
                    ),
                ): bool,
                vol.Required(
                    CONF_INCLUDE_GENERATOR,
                    default=entry.options.get(
                        CONF_INCLUDE_GENERATOR, entry.data.get(CONF_INCLUDE_GENERATOR, False)
                    ),
                ): bool,
                vol.Required(
                    CONF_INCLUDE_DIAGNOSTICS,
                    default=entry.options.get(
                        CONF_INCLUDE_DIAGNOSTICS, entry.data.get(CONF_INCLUDE_DIAGNOSTICS, True)
                    ),
                ): bool,
                vol.Required(
                    CONF_TIMEOUT,
                    default=entry.options.get(CONF_TIMEOUT, entry.data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)),
                ): vol.All(vol.Coerce(float), vol.Range(min=1, max=30)),
                vol.Required(
                    CONF_READ_RETRIES,
                    default=entry.options.get(
                        CONF_READ_RETRIES, entry.data.get(CONF_READ_RETRIES, DEFAULT_READ_RETRIES)
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
                vol.Required(
                    CONF_MAX_BLOCK,
                    default=entry.options.get(
                        CONF_MAX_BLOCK, entry.data.get(CONF_MAX_BLOCK, DEFAULT_MAX_BLOCK)
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=10, max=123)),
                vol.Required(
                    CONF_MAX_ENERGY_RATE,
                    default=entry.options.get(
                        CONF_MAX_ENERGY_RATE,
                        entry.data.get(CONF_MAX_ENERGY_RATE, DEFAULT_MAX_ENERGY_RATE),
                    ),
                ): vol.All(vol.Coerce(float), vol.Range(min=1, max=500)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)


class CannotConnect(HomeAssistantError):
    """Failed to connect to the inverter."""
