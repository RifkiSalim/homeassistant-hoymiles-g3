# Hoymiles → Home Assistant (native Modbus TCP)

Home Assistant configuration that exposes every field decoded by [wasilukm/hoymiles_modbus](https://github.com/wasilukm/hoymiles_modbus) using the built-in [Modbus integration](https://www.home-assistant.io/integrations/modbus/) only (no custom component).

## What this maps

The Python library talks to a **Hoymiles DTU-Pro / Pro-S** on **Modbus TCP port 502**, unit id **1**:

| Block | Start address (dec) | Registers read | Fields |
|-------|---------------------|----------------|--------|
| Inverter *n* | `4096 + n × 40` (`0x1000`) | 20 | PV, grid, energy, temperature, alarms, link status, … |
| DTU serial | `8192` (`0x2000`) | 3 | 6-byte DTU serial (hex) |

Per-inverter layout (byte offsets from [ `datatypes.py` ](https://github.com/wasilukm/hoymiles_modbus/blob/main/hoymiles_modbus/datatypes.py)):

| Field | Register offset from inverter base | Type | Scale |
|-------|-----------------------------------|------|-------|
| Data type | +0 | uint16 (low byte) | 1 |
| Serial number | +0 … +2 | 6 bytes (template) | — |
| Port number | +3 (low byte of reg) | — | 1 |
| PV voltage | +4 | uint16 | 0.1 → V |
| PV current | +5 | uint16 | 0.01 (HM/HIS) or 0.1 (MI, serial `10…`) |
| Grid voltage | +6 | uint16 | 0.1 → V |
| Grid frequency | +7 | uint16 | 0.01 → Hz |
| PV power | +8 | uint16 | 0.1 → W |
| Today production | +9 | uint16 | Wh |
| Total production | +10 | uint32 | Wh |
| Temperature | +12 | int16 | 0.1 → °C |
| Operating status | +13 | uint16 | — |
| Alarm code | +14 | uint16 | — |
| Alarm count | +15 | uint16 | — |
| Link status | +16 (high byte) | 0/1 | online when 1 |

Plant totals in the library sum **link_status = 1** inverters only; template sensors in this package do the same.

## HIS 5L G3 hybrid inverter

The **hoymiles_modbus** project documents the **DTU-Pro** register map (microinverter gateway), not the **DTS-WL-G3** stick used by many **G3 hybrid** installs. Your **HIS-5L-G3** will work with this configuration when Modbus TCP on port 502 reaches a **DTU-Pro/Pro-S** that lists the inverter in its plant map (Ethernet on the DTU, fixed DHCP reservation).

If your hybrid only has a **DTS-WL-G3** Ethernet dongle, that device uses a **different** register map; this package will not match it. In that case you need a map aimed at G3 hybrids (for example community G3 Modbus projects), still via native Modbus once addresses are known.

**PV current scale:** HM/HIS-style inverters use **0.01 A** (default in `packages/hoymiles_modbus.yaml`). MI series (serial starting with `10`) use **0.1 A** — change `scale` on the PV current sensor if needed.

## Install

1. Copy `homeassistant/packages/hoymiles_modbus.yaml` into your Home Assistant `config/packages/` directory (or merge into `configuration.yaml`).

2. Enable packages if you have not already:

   ```yaml
   homeassistant:
     package_dir: !include_dir_named packages
   ```

3. Set secrets (copy from `homeassistant/secrets.yaml.example`):

   ```yaml
   hoymiles_host: 192.168.1.50   # DTU-Pro IP
   hoymiles_port: 502
   hoymiles_unit: 1
   ```

4. Restart Home Assistant and check **Settings → Devices & services → Modbus**.

5. Optional: import `homeassistant/dashboards/hoymiles.yaml` as a dashboard view.

## Multiple inverters

Duplicate the `inverter_0` sensor block in `hoymiles_modbus.yaml` and add **40** to every `address` (4096 → 4136 → 4176, …). Extend the template sensors at the bottom to sum additional entities.

## DTU response quirk

Some DTUs send Modbus TCP frames with an incorrect byte-count field. The Python library patches that in software; Home Assistant’s Modbus stack may fail on those devices. If polls time out while `hoymiles_modbus` works from Python, use the [hoymiles-mqtt](https://github.com/wasilukm/hoymiles-mqtt) bridge or a small Modbus proxy that normalizes responses.

## References

- Register logic: https://github.com/wasilukm/hoymiles_modbus  
- Home Assistant Modbus: https://www.home-assistant.io/integrations/modbus/
