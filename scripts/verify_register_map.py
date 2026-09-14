#!/usr/bin/env python3
"""Verify Modbus register addresses against wasilukm/hoymiles_modbus layout."""

from __future__ import annotations

# Offsets in 16-bit holding registers from inverter base (4096 + index * 40)
FIELDS = {
    "data_type / serial start": 0,
    "pv_voltage": 4,
    "pv_current": 5,
    "grid_voltage": 6,
    "grid_frequency": 7,
    "pv_power": 8,
    "today_production": 9,
    "total_production": 10,
    "temperature": 12,
    "operating_status": 13,
    "alarm_code": 14,
    "alarm_count": 15,
    "link_status (high byte of reg)": 16,
}

DTU_SERIAL_BASE = 0x2000
INVERTER_BASE = 0x1000
INVERTER_STRIDE = 40


def main() -> None:
    print("hoymiles_modbus → Home Assistant address check\n")
    print(f"DTU serial holding registers: {DTU_SERIAL_BASE}..{DTU_SERIAL_BASE + 2}")
    base = INVERTER_BASE
    print(f"Inverter 0 base: {base} (0x{base:x})")
    for name, offset in FIELDS.items():
        addr = base + offset
        print(f"  {name:32} register {addr} (0x{addr:x})")
    print(f"\nInverter 1 base would be: {base + INVERTER_STRIDE} (add 40 per index)")


if __name__ == "__main__":
    main()
