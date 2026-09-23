# Hoymiles (Home Assistant custom integration)

Native **Home Assistant** integration for **Hoymiles G3 hybrid** inverters (HIS / HIT-xxL-G3 and similar), powered by the community register catalog in [hoymiles-g3-modbus-tcp](https://pypi.org/project/hoymiles-g3-modbus-tcp/) on PyPI.

The integration polls **Modbus TCP** (FC04 input registers and optional FC03 holding registers). Behavior is the same for:

| Connection path | Typical setup |
|-----------------|---------------|
| **DTS-WL-G3 (Ethernet)** | HA → stick on LAN → inverter (port **502**, unit **1**) |
| **External Modbus TCP gateway** | HA → NE2-D14PE (or similar) on **485_2** → inverter |

Only the **host, port, and unit ID** change between paths; register decoding and entity layout are identical.

## Install

Home Assistant discovers integrations under **`config/custom_components/`** after a restart. This integration does not require HACS.

### Manual

Copy `custom_components/hoymiles` into your HA `config/custom_components/` directory and restart. Then **Settings → Devices & services → Add integration → Hoymiles**.

### HACS (optional)

If you use the [Home Assistant Community Store](https://hacs.xyz/), add this GitHub repo as a custom repository (category **Integration**), install **Hoymiles**, and restart. HACS’s “custom repository” UI is a HACS feature, not a core Home Assistant feature.

## Configuration

**Initial setup**

- **Connection path** — Labels how you wired the system (does not change the protocol).
- **Host / port / unit** — IP and Modbus TCP port of the stick or gateway (default port **502**, unit **1**).

**Options** (Configure on the integration entry)

| Option | Purpose |
|--------|---------|
| Sensor set | **Minimal**, **Standard** (default), or **Full** entity sets |
| Fast / slow poll intervals | Tiered polling (power flows vs energy/status) |
| Configuration registers | Expose holding registers (read-only) as sensors |
| Generator / diagnostics | Optional entity groups |
| Timeout, retries, block size | Tune for noisy links or slow gateways |

Changing options reloads the integration automatically.

## Device brand

Entities are grouped under one device with manufacturer **Hoymiles**, model detected from the inverter (e.g. HIS-5L-G3).

## Dependencies

`hoymiles-g3-modbus-tcp==0.3.0` is installed automatically by Home Assistant when the integration loads.

## License

MIT — see repository root `LICENSE`.
