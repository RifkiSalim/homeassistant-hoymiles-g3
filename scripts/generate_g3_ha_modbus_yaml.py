#!/usr/bin/env python3
"""Generate Home Assistant native Modbus YAML for Hoymiles G3 hybrid (input registers)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".local/lib/python3.12/site-packages"))

from hoymiles_g3_modbus_tcp.registers import REGISTERS, SYNTHETIC_BASE, WSIZE  # noqa: E402

HA_DTYPE = {
    "U16": "uint16",
    "I16": "int16",
    "U32": "uint32",
    "I32": "int32",
    "H32": "uint32",
    "I32R": "int32",
    "F32": "float32",
}


def ha_scale(reg_scale: float) -> float:
    return 1.0 / reg_scale if reg_scale else 1.0


def precision(scale: float) -> int:
    if scale >= 1:
        return 0
    s = f"{scale:.10f}".rstrip("0")
    return len(s.split(".")[-1]) if "." in s else 0


def device_class(unit: str | None, key: str) -> str | None:
    if unit == "V":
        return "voltage"
    if unit == "A":
        return "current"
    if unit == "W":
        return "power"
    if unit == "Hz":
        return "frequency"
    if unit == "°C" or key.endswith("_temp"):
        return "temperature"
    if unit == "kWh" or unit == "Wh":
        return "energy"
    if unit == "%" and "soc" in key:
        return "battery"
    return None


def state_class(unit: str | None, key: str) -> str | None:
    if unit in ("W", "V", "A", "Hz", "Var", "VA"):
        return "measurement"
    if unit in ("kWh", "Wh") and "today" in key:
        return "total_increasing"
    if unit in ("kWh", "Wh") and ("total" in key or "lifetime" in key or "energy" in key):
        return "total_increasing"
    if key.endswith("_soc"):
        return "measurement"
    return None


def scan_interval(addr: int) -> int:
    if addr >= 30000:
        return 30
    if addr >= 2000:
        return 60
    return 10


def emit_sensor(reg, lines: list[str]) -> None:
    if reg.addr >= SYNTHETIC_BASE or reg.source:
        return
    if reg.kind != "input":
        return
    dtype = HA_DTYPE.get(reg.dtype)
    if not dtype:
        return

    scale = ha_scale(reg.scale)
    name = reg.label.replace("'", "")
    uid = f"hoymiles_g3_{reg.key}"
    lines.append(f"      - name: Hoymiles {name}")
    lines.append(f"        unique_id: {uid}")
    lines.append("        slave: !secret hoymiles_unit")
    lines.append(f"        address: {reg.addr}")
    lines.append("        input_type: input")
    lines.append(f"        data_type: {dtype}")
    if scale != 1.0:
        lines.append(f"        scale: {scale}")
        prec = precision(scale)
        if prec:
            lines.append(f"        precision: {prec}")
    if reg.unit:
        lines.append(f"        unit_of_measurement: {reg.unit}")
    dc = device_class(reg.unit, reg.key)
    if dc:
        lines.append(f"        device_class: {dc}")
    sc = state_class(reg.unit, reg.key)
    if sc:
        lines.append(f"        state_class: {sc}")
    lines.append(f"        scan_interval: {scan_interval(reg.addr)}")
    lines.append("")


def main() -> None:
    lines = [
        "# Hoymiles G3 hybrid (HIS/HIT-xxL-G3) — native Modbus INPUT registers",
        "# Register map: hoymiles-g3-modbus-tcp/registers.py (community, verified on HIT-15L-G3)",
        "#",
        "# DISABLE packages/hoymiles_modbus.yaml (DTU-Pro 0x1000 map) before using this file.",
        "",
        "modbus:",
        "  - name: hoymiles_gateway",
        "    type: tcp",
        "    host: !secret hoymiles_host",
        "    port: !secret hoymiles_port",
        "    timeout: 5",
        "    retries: 3",
        "    delay: 1",
        "    sensors:",
    ]

    for reg in REGISTERS:
        emit_sensor(reg, lines)

    lines.extend(
        [
            "",
            "template:",
            "  - sensor:",
            "      - name: Hoymiles PV total power (computed)",
            "        unique_id: hoymiles_g3_pv_total_power_computed",
            "        unit_of_measurement: W",
            "        device_class: power",
            "        state_class: measurement",
            "        state: >",
            "          {{",
            "            states('sensor.hoymiles_pv1_power') | float(0)",
            "            + states('sensor.hoymiles_pv2_power') | float(0)",
            "            + states('sensor.hoymiles_pv3_power') | float(0)",
            "            + states('sensor.hoymiles_pv4_power') | float(0)",
            "          }}",
        ]
    )

    out = Path(__file__).resolve().parents[1] / "homeassistant/packages/hoymiles_g3_hybrid.yaml"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    count = sum(
        1
        for r in REGISTERS
        if r.addr < SYNTHETIC_BASE and not r.source and r.kind == "input" and r.dtype in HA_DTYPE
    )
    print(f"Wrote {out} ({count} modbus sensors)")


if __name__ == "__main__":
    main()
