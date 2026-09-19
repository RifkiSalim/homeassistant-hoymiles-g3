# Hoymiles G3 hybrid → Home Assistant

Home Assistant **custom integration** for **Hoymiles G3 hybrid** inverters (HIS / HIT-xxL-G3 and similar). It uses the community [hoymiles-g3-modbus-tcp](https://pypi.org/project/hoymiles-g3-modbus-tcp/) library for Modbus TCP polling and register decoding.

## Install

### HACS

1. Add this repository as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories/) (category: **Integration**).
2. Install **Hoymiles** and restart Home Assistant.
3. **Settings → Devices & services → Add integration → Hoymiles**.

### Manual

Copy `custom_components/hoymiles` into your Home Assistant `config/custom_components/` directory and restart.

Details and options: [custom_components/hoymiles/README.md](custom_components/hoymiles/README.md).

## Supported hardware

- **Inverters:** G3 hybrid models (e.g. HIS-5L-G3, HIT-xxL-G3).
- **Modbus paths (same integration, same entities):**
  - **DTS-WL-G3** data stick on **Ethernet** (typical port **502**, unit **1**).
  - **External Modbus TCP gateway** on the inverter **485_2** port (e.g. NE2-D14PE).

Use one Modbus client only — do not poll the same host/port from another integration at the same time.

## Wiring (DTS Ethernet)

| Topic | Detail |
|--------|--------|
| Modbus TCP | Stick **Ethernet** port, usually **502**, unit **1**. |
| Wi‑Fi | App/cloud; Modbus TCP is not on Wi‑Fi for these sticks. |
| LAN | Stick → wired LAN → Home Assistant. |

## Troubleshooting

**Cannot connect** — From the HA host: `nc -zv INVERTER_OR_STICK_IP 502`. Confirm Ethernet IP, not Wi‑Fi.

**Stale or missing sensors** — Increase timeout/retries in integration options; check firewall and duplicate Modbus clients.

## References

- Register catalog: https://pypi.org/project/hoymiles-g3-modbus-tcp/

## License

MIT — see [LICENSE](LICENSE).
