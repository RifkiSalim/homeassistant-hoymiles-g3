# Hoymiles (Home Assistant custom integration)

Native **Home Assistant** integration for **Hoymiles G3 hybrid** inverters (HIS / HIT-xxL-G3 and similar), powered by the community register catalog in [hoymiles-g3-modbus-tcp](https://pypi.org/project/hoymiles-g3-modbus-tcp/) on PyPI.

The integration polls **Modbus TCP** (FC04 input registers and optional FC03 holding registers). Behavior is the same for:

| Connection path | Typical setup |
|-----------------|---------------|
| **DTS-WL-G3 (Ethernet)** | HA → stick on LAN → inverter (port **502**, unit **1**) |
| **External Modbus TCP gateway** | HA → NE2-D14PE (or similar) on **485_2** → inverter |

Only the **host, port, and unit ID** change between paths; register decoding and entity layout are identical.

## Install

### HACS (recommended)

1. Add this repository as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories/) (category: **Integration**).
2. Install **Hoymiles**.
3. Restart Home Assistant.
4. **Settings → Devices & services → Add integration → Hoymiles**.

### Manual

Copy the `custom_components/hoymiles` folder into your HA `config/custom_components/` directory and restart.

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

## Migration from YAML Modbus package

If you use `homeassistant/packages/hoymiles_g3_hybrid.yaml` in this repo, **disable that package** and remove duplicate custom integrations before adding **Hoymiles**, so a single client polls the inverter.

## Dependencies

`hoymiles-g3-modbus-tcp==0.3.0` is installed automatically by Home Assistant when the integration loads.

## License

MIT — see repository root `LICENSE`.
