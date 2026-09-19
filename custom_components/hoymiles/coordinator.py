"""Hoymiles G3 hybrid Modbus coordinator."""

from __future__ import annotations

import logging
import time
from datetime import timedelta

from hoymiles_g3_modbus_tcp import Inverter, InverterConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_INCLUDE_SETTINGS,
    CONF_MAX_BLOCK,
    CONF_MAX_ENERGY_RATE,
    CONF_READ_RETRIES,
    CONF_SLOW_INTERVAL,
    CONF_TIMEOUT,
    CONF_UNIT,
    DEFAULT_MAX_BLOCK,
    DEFAULT_MAX_ENERGY_RATE,
    DEFAULT_READ_RETRIES,
    DEFAULT_SLOW_INTERVAL,
    DEFAULT_TIMEOUT,
    DEFAULT_UNIT,
    DOMAIN,
    SLOW_GROUPS,
)

_LOGGER = logging.getLogger(__name__)


class HoymilesCoordinator(DataUpdateCoordinator[dict]):
    """Poll inverter via hoymiles-g3-modbus-tcp tiered groups."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        fast = entry.options.get("fast_scan_interval", entry.data.get("fast_scan_interval", 10))
        self._slow_interval = entry.options.get(
            "slow_scan_interval", entry.data.get("slow_scan_interval", DEFAULT_SLOW_INTERVAL)
        )
        self._include_settings = entry.options.get(
            CONF_INCLUDE_SETTINGS, entry.data.get(CONF_INCLUDE_SETTINGS, False)
        )
        self._last_slow_poll = 0.0
        config = InverterConfig(
            host=entry.data["host"],
            port=entry.data["port"],
            unit=entry.data.get(CONF_UNIT, DEFAULT_UNIT),
            timeout=entry.options.get(CONF_TIMEOUT, entry.data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)),
            max_block=entry.options.get(CONF_MAX_BLOCK, entry.data.get(CONF_MAX_BLOCK, DEFAULT_MAX_BLOCK)),
            read_retries=entry.options.get(
                CONF_READ_RETRIES, entry.data.get(CONF_READ_RETRIES, DEFAULT_READ_RETRIES)
            ),
            max_energy_rate=entry.options.get(
                CONF_MAX_ENERGY_RATE,
                entry.data.get(CONF_MAX_ENERGY_RATE, DEFAULT_MAX_ENERGY_RATE),
            ),
        )
        self.inverter = Inverter(config)
        self.inverter_info = None
        self.config_entry = entry
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(seconds=fast),
        )

    async def async_setup(self) -> None:
        await self.inverter.connect()
        self.inverter_info = await self.inverter.detect()

    async def _async_update_data(self) -> dict:
        try:
            await self.inverter.poll_group("fast")
            now = time.monotonic()
            if now - self._last_slow_poll >= self._slow_interval:
                for group in SLOW_GROUPS:
                    await self.inverter.poll_group(group)
                if self._include_settings:
                    await self.inverter.poll_group("settings")
                self._last_slow_poll = now
            return self.inverter.snapshot()
        except Exception as err:
            raise UpdateFailed(f"Modbus poll failed: {err}") from err

    async def async_shutdown(self) -> None:
        await self.inverter.close()
