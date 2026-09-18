# Hoymiles G3 hybrid → Home Assistant (native Modbus TCP)

Home Assistant **YAML only** (built-in [Modbus](https://www.home-assistant.io/integrations/modbus/) integration) for **HIS / HIT-xxL-G3** hybrids using the factory **data transfer stick (DTS / “DTU stick”)** on **Ethernet**.

No custom component, no RS485 gateway (e.g. NE2-D14PE) required for Modbus if the stick is on LAN via **RJ45**.

## Recommended wiring (your setup)

```text
Home Assistant  --Modbus TCP :502-->  DTS-WL-G3 (Ethernet)  --internal link-->  HIS-5L-G3
```

Important details from community G3 Modbus work ([hoymiles-g3-modbus-tcp](https://pypi.org/project/hoymiles-g3-modbus-tcp/)):

| Topic | Detail |
|--------|--------|
| **Modbus TCP** | Available on the stick’s **Ethernet** port (port **502**, unit id **1** typical). |
| **Wi‑Fi** | Cloud/app use; **Modbus TCP is not exposed on Wi‑Fi** on these sticks. |
| **Register map** | G3 **input registers (FC04)**, addresses from the G3 catalog (e.g. PV1 voltage **27**, grid frequency **66**, battery SOC **1909**) — **not** the DTU‑Pro **0x1000** holding map. |
| **Package to use** | `homeassistant/packages/hoymiles_g3_hybrid.yaml` |

Set `secrets.yaml`:

```yaml
hoymiles_host: 192.168.x.x   # DHCP reservation for the stick’s Ethernet IP
hoymiles_port: 502
hoymiles_unit: 1
```

Use a **wired Ethernet** path from the stick to the same LAN as Home Assistant (stick → switch/router → HA). Do not point HA at the stick’s Wi‑Fi address if you need Modbus.

## Install

1. Copy `homeassistant/packages/hoymiles_g3_hybrid.yaml` → `config/packages/`.
2. **Do not** load `hoymiles_modbus.yaml` for a G3 hybrid (that file is for **DTU‑Pro microinverter** plants at holding register **4096**; wrong map causes bogus values like **0.1 V** / **2 Hz**).
3. Enable packages in `configuration.yaml`:

   ```yaml
   homeassistant:
     package_dir: !include_dir_named packages
   ```

4. Merge `homeassistant/secrets.yaml.example` into `secrets.yaml`.
5. **Check configuration** → restart.
6. Optional dashboard: `homeassistant/dashboards/hoymiles_g3.yaml`.

Disable duplicate Hoymiles **custom** integrations (e.g. `hoymiles_modbus_tcp`) if you use this YAML, so one client polls the stick.

## Register map source (G3 hybrid)

Sensors in `hoymiles_g3_hybrid.yaml` are generated from **`hoymiles_g3_modbus_tcp/registers.py`** ([PyPI](https://pypi.org/project/hoymiles-g3-modbus-tcp/), community catalog aligned with hardware such as HIT-15L-G3). Regenerate after catalog updates:

```bash
pip install hoymiles-g3-modbus-tcp
python3 scripts/generate_g3_ha_modbus_yaml.py
```

That map is independent of [wasilukm/hoymiles_modbus](https://github.com/wasilukm/hoymiles_modbus), which documents **DTU‑Pro/Pro-S** microinverter telemetry at **0x1000**.

## Optional: other hardware paths

| Path | Package |
|------|---------|
| **DTU‑Pro / Pro-S** microinverter plant (Ethernet, holding **0x1000**) | `hoymiles_modbus.yaml` |
| DTU serial @ **0x2000** on DTU‑Pro | `hoymiles_modbus_dtu_gateway.yaml` |
| USB **RS485** on the HA host (RTU, not TCP) | `hoymiles_modbus_rtu_serial.yaml.example` |
| Third‑party **485_2** gateway (legacy / VPP port) | Same **G3 input** map if the gateway forwards FC04 unchanged; otherwise use gateway docs |

You do **not** need an external Modbus TCP-to-RS485 device on **485_2** if the **DTS Ethernet Modbus** path works.

## Troubleshooting

**`unknown` sensors** — HA cannot open TCP to `hoymiles_host:hoymiles_port` (wrong IP, Wi‑Fi instead of Ethernet, firewall, stick offline). From the HA host:

```bash
nc -zv YOUR_STICK_IP 502
```

**Wrong numbers** — Usually means `hoymiles_modbus.yaml` (DTU‑Pro map) is still loaded; switch to `hoymiles_g3_hybrid.yaml` only.

**YAML error `found character '%'`** — Use the latest `hoymiles_g3_hybrid.yaml` (units quoted, e.g. `unit_of_measurement: "%"`).

**Template `&` / `>>` errors** — Only in `hoymiles_modbus.yaml` templates; G3 package does not use those.

## References

- G3 register catalog: https://pypi.org/project/hoymiles-g3-modbus-tcp/
- DTU‑Pro map (microinverters): https://github.com/wasilukm/hoymiles_modbus
- Home Assistant Modbus: https://www.home-assistant.io/integrations/modbus/
