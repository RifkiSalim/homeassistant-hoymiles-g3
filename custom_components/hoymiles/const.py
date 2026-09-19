"""Constants for the Hoymiles integration."""

from __future__ import annotations

import re

from hoymiles_g3_modbus_tcp.registers import REGISTERS, SYNTHETIC_BASE

DOMAIN = "hoymiles"
MANUFACTURER = "Hoymiles"

CONF_CONNECTION_TYPE = "connection_type"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_UNIT = "unit"
CONF_TIMEOUT = "timeout"
CONF_READ_RETRIES = "read_retries"
CONF_MAX_BLOCK = "max_block"
CONF_MAX_ENERGY_RATE = "max_energy_rate"
CONF_FAST_INTERVAL = "fast_scan_interval"
CONF_SLOW_INTERVAL = "slow_scan_interval"
CONF_SENSOR_PROFILE = "sensor_profile"
CONF_INCLUDE_SETTINGS = "include_settings"
CONF_INCLUDE_GENERATOR = "include_generator"
CONF_INCLUDE_DIAGNOSTICS = "include_diagnostics"

CONNECTION_DTS_ETHERNET = "dts_ethernet"
CONNECTION_MODBUS_GATEWAY = "modbus_gateway"

CONNECTION_TYPES = {
    CONNECTION_DTS_ETHERNET: "DTS-WL-G3 (Ethernet Modbus TCP)",
    CONNECTION_MODBUS_GATEWAY: "External Modbus TCP gateway (e.g. RS485 on 485_2)",
}

DEFAULT_PORT = 502
DEFAULT_UNIT = 1
DEFAULT_TIMEOUT = 3.0
DEFAULT_READ_RETRIES = 3
DEFAULT_MAX_BLOCK = 123
DEFAULT_MAX_ENERGY_RATE = 100.0
DEFAULT_FAST_INTERVAL = 10
DEFAULT_SLOW_INTERVAL = 60

PROFILE_MINIMAL = "minimal"
PROFILE_STANDARD = "standard"
PROFILE_FULL = "full"

SLOW_GROUPS = ("energy", "status", "battery", "diagnostics")

SKIP_REGISTER_KEYS = frozenset(
    {
        "load_energy_total",
        "pv_ths_temp",
        "ext_fan_1",
        "ext_fan_2",
        "ext_fan_3",
        "ext_fan_4",
        "pv_power",
    }
)

_PV_STRING_NUM = re.compile(r"^pv([1-4])_")


def _pv_string_index(key: str) -> int | None:
    m = _PV_STRING_NUM.match(key)
    return int(m.group(1)) if m else None


def iter_exposed_registers(
    *,
    profile: str,
    include_settings: bool,
    include_generator: bool,
    include_diagnostics: bool,
    has_battery: bool,
    has_grid_meter: bool,
    pv_mppt_count: int,
) -> list:
    """Return register definitions to expose as entities."""
    mppt = max(pv_mppt_count, 1)

    if profile == PROFILE_MINIMAL:
        allowed_domains = {"pv", "grid", "ac", "backup", "energy", "status"}
    elif profile == PROFILE_STANDARD:
        allowed_domains = {
            "pv",
            "grid",
            "ac",
            "backup",
            "energy",
            "status",
            "battery",
            "grid_meter",
            "inverter",
            "generator",
        }
    else:
        allowed_domains = None

    if has_battery:
        allowed_domains = (allowed_domains or set()) | {"battery"}
    if has_grid_meter:
        allowed_domains = (allowed_domains or set()) | {"grid_meter"}

    if not include_generator and allowed_domains is not None:
        allowed_domains.discard("generator")
    if not include_diagnostics and allowed_domains is not None:
        allowed_domains.discard("inverter")

    out = []
    for reg in REGISTERS:
        if reg.key in SKIP_REGISTER_KEYS:
            continue
        if not include_diagnostics and reg.domain == "inverter":
            continue
        if reg.kind == "holding" and not include_settings:
            continue
        if reg.domain == "settings" and not include_settings:
            continue
        if not has_battery and reg.domain == "battery":
            continue
        if not has_grid_meter and reg.domain == "grid_meter":
            continue
        if not include_generator and reg.domain == "generator":
            continue
        if allowed_domains is not None and reg.domain not in allowed_domains:
            continue
        pv_idx = _pv_string_index(reg.key)
        if pv_idx is not None and pv_idx > mppt:
            continue
        if reg.addr >= SYNTHETIC_BASE and not reg.source:
            continue
        out.append(reg)
    return out
