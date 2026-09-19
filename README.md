# Hoymiles G3 hybrid → Home Assistant

Open-source **Home Assistant** support for **HIS / HIT-xxL-G3** hybrids using the community [hoymiles-g3-modbus-tcp](https://pypi.org/project/hoymiles-g3-modbus-tcp/) register catalog.

## Recommended: custom integration (Hoymiles)

Install the **`custom_components/hoymiles`** integration (HACS or manual copy). It adds the **Hoymiles** brand in the UI, auto-detects MPPT/battery/meter capabilities, and exposes configurable sensor sets and polling options.

Works the same over:

```text
Home Assistant  --Modbus TCP :502-->  DTS-WL-G3 (Ethernet)  -->  inverter
Home Assistant  --Modbus TCP :502-->  RS485 gateway on 485_2  -->  inverter
```

See [custom_components/hoymiles/README.md](custom_components/hoymiles/README.md) for setup and options.

**Do not** run this integration together with another Hoymiles Modbus client (YAML package or other custom integrations) on the same host/port.

## Legacy: YAML Modbus package

The repo still includes a generated **native Modbus** YAML package if you prefer not to use a custom integration:

| File | Use case |
|------|-----------|
| `homeassistant/packages/hoymiles_g3_hybrid.yaml` | G3 hybrid **input register** map (FC04) |
| `homeassistant/packages/hoymiles_modbus.yaml` | DTU‑Pro **microinverter** map @ **0x1000** — **not** for G3 hybrids |

Regenerate the G3 YAML after catalog updates:

```bash
pip install hoymiles-g3-modbus-tcp
python3 scripts/generate_g3_ha_modbus_yaml.py
```

Set `secrets.yaml` from `homeassistant/secrets.yaml.example` (`hoymiles_host`, port **502**, unit **1**).

## Wiring notes (DTS Ethernet)

| Topic | Detail |
|--------|--------|
| **Modbus TCP** | Stick **Ethernet** port, typically **502**, unit **1**. |
| **Wi‑Fi** | App/cloud; Modbus TCP is not on Wi‑Fi for these sticks. |
| **Register map** | G3 **input** catalog (e.g. PV1 V @ **27**, grid Hz @ **66**) — not DTU‑Pro **0x1000**. |

Use a wired path: stick → LAN → Home Assistant.

## Troubleshooting

**Cannot connect** — Verify IP/port from the HA host (`nc -zv HOST 502`). Use the stick’s **Ethernet** IP, not Wi‑Fi.

**Wrong values** — Wrong register map (DTU‑Pro YAML on a G3 hybrid) or a second client polling the same device.

## References

- PyPI library: https://pypi.org/project/hoymiles-g3-modbus-tcp/
- DTU‑Pro map (microinverters): https://github.com/wasilukm/hoymiles_modbus
- Home Assistant Modbus: https://www.home-assistant.io/integrations/modbus/

## License

MIT — see [LICENSE](LICENSE).
