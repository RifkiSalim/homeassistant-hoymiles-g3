# Hoymiles G3 hybrid for Home Assistant

Custom integration for **Hoymiles G3 hybrid** inverters (HIS / HIT-xxL-G3 and similar). Polls the inverter over **Modbus TCP** using the community [hoymiles-g3-modbus-tcp](https://pypi.org/project/hoymiles-g3-modbus-tcp/) register catalog.

**Repository:** https://github.com/RifkiSalim/homeassistant-hoymiles-g3

## Install

### HACS

1. HACS → **Integrations** → **⋮** → **Custom repositories** → add `RifkiSalim/homeassistant-hoymiles-g3` (category **Integration**).
2. Install **Hoymiles** and restart Home Assistant.
3. **Settings → Devices & services → Add integration → Hoymiles**.

### Manual

Clone https://github.com/RifkiSalim/homeassistant-hoymiles-g3, copy `custom_components/hoymiles` into your Home Assistant `config/custom_components/` directory, and restart.

Integration options and connection notes: [custom_components/hoymiles/README.md](custom_components/hoymiles/README.md).

## Supported hardware

| | |
|--|--|
| **Inverters** | G3 hybrids (e.g. HIS-5L-G3, HIT-xxL-G3) |
| **DTS-WL-G3 (Ethernet)** | Modbus TCP on LAN, typically port **502**, unit **1** |
| **RS485 gateway on 485_2** | External Modbus TCP gateway (e.g. NE2-D14PE); same integration settings apart from host/port |

Use **one** Modbus client per host/port (do not run a second integration or YAML Modbus stack against the same endpoint).

## Wiring (DTS Ethernet stick)

| Topic | Detail |
|--------|--------|
| Modbus TCP | Stick **Ethernet** port, usually **502**, unit **1** |
| Wi‑Fi | App/cloud only; Modbus TCP is not on Wi‑Fi for these sticks |
| LAN | Stick → wired LAN → Home Assistant |

## Troubleshooting

| Symptom | What to check |
|--------|----------------|
| Cannot connect | From the HA host: `nc -zv HOST 502`. Use the stick’s **Ethernet** IP, not Wi‑Fi. |
| Missing or stale values | Increase timeout/retries in integration options; rule out firewall and duplicate Modbus clients. |

## References

- Register catalog: https://pypi.org/project/hoymiles-g3-modbus-tcp/

## License

MIT — see [LICENSE](LICENSE).
