# Hoymiles G3 hybrid → Home Assistant

Home Assistant **custom integration** for **Hoymiles G3 hybrid** inverters (HIS / HIT-xxL-G3 and similar). It uses the community [hoymiles-g3-modbus-tcp](https://pypi.org/project/hoymiles-g3-modbus-tcp/) library for Modbus TCP polling and register decoding.

## Sync to GitHub

This project is hosted on **Cursor Origin** at [homeassistant-hoymiles-g3](https://cursor.com/codebase/rifki-salim/homeassistant-hoymiles-g3). GitHub is not connected yet (`mirrorStatus: no-mirror`). To publish the same history on GitHub:

### Prerequisites

1. **Cursor ↔ GitHub** — In Cursor, connect the [GitHub integration](https://cursor.com/settings) (GitHub App with access to your account/org).
2. **Origin CLI** on your machine (clone URL uses your login):

```bash
curl -fsSL https://downloads.cursor.com/origin/install.sh | sh
origin auth login
```

If `origin` is not found:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Origin CLI reference: https://cursor.com/docs/origin/cli

### Option A — Push to a new GitHub repo (simple)

Create an **empty** repository on GitHub named `homeassistant-hoymiles-g3` (no README/license/gitignore), then:

```bash
origin repo clone rifki-salim/homeassistant-hoymiles-g3
cd homeassistant-hoymiles-g3
git remote add github https://github.com/rifki-salim/homeassistant-hoymiles-g3.git
git push -u github main
```

Use your GitHub username/org in the `github` remote URL if it differs.

### Option B — Link GitHub as source of truth in Cursor (ongoing sync)

After the repo exists on GitHub with `main` pushed:

1. Open https://cursor.com/codebase
2. Choose **Sync from GitHub**
3. Select `rifki-salim/homeassistant-hoymiles-g3`

GitHub becomes the source of truth; `git push` to the Origin HTTPS remote goes to GitHub and Origin updates afterward. See [Mirror a GitHub repository](https://cursor.com/docs/origin/mirror-github).

To keep pushing to **both** remotes from one `origin` remote:

```bash
git remote set-url --add --push origin https://github.com/rifki-salim/homeassistant-hoymiles-g3.git
git remote set-url --add --push origin https://origin.cursor.com/rifki-salim/homeassistant-hoymiles-g3.git
```

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
