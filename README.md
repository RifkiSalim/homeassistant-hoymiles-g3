# Hoymiles → Home Assistant (native Modbus TCP)

Home Assistant configuration that exposes every field decoded by [wasilukm/hoymiles_modbus](https://github.com/wasilukm/hoymiles_modbus) using the built-in [Modbus integration](https://www.home-assistant.io/integrations/modbus/) only (no custom component).

## What this maps

The Python library talks to a device that speaks **Hoymiles DTU-Pro Modbus** on **port 502**. In your setup that device is the **external DTU** on the inverter’s **485_2** port (COM2), with Home Assistant reaching it over **Modbus TCP** on the DTU’s Ethernet/Wi‑Fi interface (or via a USB RS485 adapter — see below).

| Block | Start address (dec) | Registers read | Fields |
|-------|---------------------|----------------|--------|
| Inverter *n* | `4096 + n × 40` (`0x1000`) | 20 | PV, grid, energy, temperature, alarms, link status, … |
| DTU serial (optional) | `8192` (`0x2000`) | 3 | 6-byte DTU serial — only on real DTU-Pro gateways |

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

## External DTU on **485_2** (your wiring)

On the **HIS-5L-G3**, COM2 includes a **485_2** pair labelled for third‑party / VPP control (see the HIS user manual). A common pattern is:

```text
Home Assistant  --Modbus TCP-->  external DTU (Ethernet)  --RS485_2-->  HIS-5L-G3
```

Configure secrets as follows:

| Secret | Value |
|--------|--------|
| `hoymiles_host` | IP of the **external DTU / TCP gateway**, not the inverter |
| `hoymiles_port` | Usually `502` |
| `hoymiles_unit` | Modbus **slave ID** on the RS485 side (try `1` first; DTU‑Pro RS485 “Hoymiles Modbus” mode often uses **101–254**) |

RS485 wiring: use the **485_2 A/B** terminals on COM2; match polarity with the DTU manual. Many Hoymiles RS485 links use **9600 8‑N‑1** — set the same on the gateway and in the inverter/VPP settings if exposed in S‑Miles Toolkit.

**Map fit:** [wasilukm/hoymiles_modbus](https://github.com/wasilukm/hoymiles_modbus) documents the **DTU‑Pro microinverter plant** layout starting at **0x1000**. It does **not** include hybrid‑only data (battery SOC, grid import/export, EPS, etc.). After install, confirm the map matches your bus:

1. Read holding register **4100** (PV voltage, scale 0.1 V) — expect a plausible AC/PV voltage when the sun is up.
2. If reads fail or values are nonsense, your gateway is probably exposing the **native G3 hybrid map** on 485_2 instead; you would need that register table (not this 0x1000 block) while still using native Modbus in HA.

Optional files:

- `packages/hoymiles_modbus_dtu_gateway.yaml` — DTU serial @ **0x2000** (enable only for a real Hoymiles DTU‑Pro class gateway).
- `packages/hoymiles_modbus_rtu_serial.yaml.example` — USB RS485 on the HA host instead of Modbus TCP.

**PV current scale:** HM/HIS-style inverters use **0.01 A** (default in `packages/hoymiles_modbus.yaml`). MI series (serial starting with `10`) use **0.1 A** — change `scale` on the PV current sensor if needed.

## Install

**HIS / HIT G3 hybrid (your 485_2 + external DTU):** use `homeassistant/packages/hoymiles_g3_hybrid_modbus.yaml` — **not** `hoymiles_modbus.yaml`. See [docs/troubleshooting-unknown.md](docs/troubleshooting-unknown.md) if sensors show `unknown`.

**DTU-Pro microinverter plant (Ethernet, 0x1000 holding map):** use `homeassistant/packages/hoymiles_modbus.yaml`.

1. Copy the correct package into your Home Assistant `config/packages/` directory (only one of the two above).

2. Enable packages if you have not already:

   ```yaml
   homeassistant:
     package_dir: !include_dir_named packages
   ```

3. Set secrets (copy from `homeassistant/secrets.yaml.example`):

   ```yaml
   hoymiles_host: 192.168.1.50   # external DTU / Modbus TCP gateway on 485_2
   hoymiles_port: 502
   hoymiles_unit: 1              # RS485 slave ID on the bus
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
