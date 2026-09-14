# Modbus sensors show `unknown`

## HIS-5L-G3 on external DTU / 485_2 (most common)

**Symptom:** `Hoymiles inv0 grid voltage` (and most `inv0` entities) stay **unknown**.

**Cause:** `hoymiles_modbus.yaml` uses the **DTU-Pro microinverter** map: **holding** registers starting at **4096**. The **G3 hybrid** exposes live data on **input** registers (Modbus function **4**), e.g. grid voltage at **input 62**, not holding **4102**.

**Fix:**

1. Remove or rename `packages/hoymiles_modbus.yaml` (only one file may define the `hoymiles_gateway` hub).
2. Copy `packages/hoymiles_g3_hybrid_modbus.yaml` into `config/packages/`.
3. Check configuration and restart.
4. Confirm **Hoymiles grid voltage** (input **62**) shows ~230 V when on grid.

## Connection / unit ID

If **all** Modbus entities are unknown:

- Ping the gateway IP; port **502** must be open from the HA host.
- Try `hoymiles_unit: 1`, then **101–254** if your gateway docs say so.
- Match RS485 **9600 8-N-1** on gateway and inverter/VPP settings.
- Read **Settings → System → Logs** and filter `modbus` for `Illegal`, `timeout`, or `connection`.

## Wrong register type

Reading an **input** address as **holding** (or the reverse) often yields **unknown** or errors. G3 telemetry uses `input_type: input` in YAML.
