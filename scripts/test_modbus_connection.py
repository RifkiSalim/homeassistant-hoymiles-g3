#!/usr/bin/env python3
"""Quick Modbus TCP check using the same addresses as homeassistant/packages/hoymiles_modbus.yaml.

Usage:
  pip install pymodbus
  python3 scripts/test_modbus_connection.py --host 192.168.1.50 --unit 1

Exits 0 when holding registers at 0x1000 decode like wasilukm/hoymiles_modbus.
"""

from __future__ import annotations

import argparse
import sys

INVERTER_BASE = 0x1000
REG_COUNT = 20
DTU_SERIAL_BASE = 0x2000


def main() -> int:
    parser = argparse.ArgumentParser(description="Test Hoymiles Modbus TCP (hoymiles_modbus map)")
    parser.add_argument("--host", required=True, help="External DTU / Modbus TCP gateway IP")
    parser.add_argument("--port", type=int, default=502)
    parser.add_argument("--unit", type=int, default=1, help="Modbus slave / unit ID on RS485")
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()

    try:
        from pymodbus.client import ModbusTcpClient
    except ImportError:
        print("Install pymodbus: pip install pymodbus", file=sys.stderr)
        return 2

    client = ModbusTcpClient(host=args.host, port=args.port, timeout=args.timeout)
    if not client.connect():
        print(f"FAIL: could not connect to {args.host}:{args.port}")
        return 1

    try:
        inv = client.read_holding_registers(INVERTER_BASE, count=REG_COUNT, device_id=args.unit)
        if inv.isError():
            print(f"FAIL: inverter block @ {INVERTER_BASE} (0x{INVERTER_BASE:x}): {inv}")
            return 1

        regs = inv.registers
        pv_v = regs[4] * 0.1
        pv_p = regs[8] * 0.1
        grid_v = regs[6] * 0.1
        link = (regs[16] >> 8) & 0xFF if len(regs) > 16 else -1

        print(f"OK: read {REG_COUNT} holding registers from {INVERTER_BASE} (unit {args.unit})")
        print(f"  PV voltage (reg+4):  {pv_v:.1f} V  (raw {regs[4]})")
        print(f"  Grid voltage (reg+6): {grid_v:.1f} V  (raw {regs[6]})")
        print(f"  PV power (reg+8):    {pv_p:.1f} W  (raw {regs[8]})")
        print(f"  Link status (high byte reg+16): {link}")

        dtu = client.read_holding_registers(DTU_SERIAL_BASE, count=3, device_id=args.unit)
        if not dtu.isError():
            print(f"OK: DTU serial block @ {DTU_SERIAL_BASE} readable (optional in HA)")
        else:
            print(f"NOTE: DTU serial @ {DTU_SERIAL_BASE} not readable (normal for 485_2 gateway-only)")
    finally:
        client.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
