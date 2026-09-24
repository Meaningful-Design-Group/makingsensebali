# Retired firmware

Nothing in this folder should be flashed. **Flash [`../diy_node_v3/`](../diy_node_v3/).**

These are kept because they are what the nodes currently in the field were flashed
with, and because the lineage explains why v3 looks the way it does. Each step moved
one more thing out of the source file and into the phone.

| | Portal asks for | Token | Reopen the portal by |
|---|---|---|---|
| [`diy_node_v1.1/`](diy_node_v1.1/) | WiFi | Hardcoded — `SC_DEVICE_TOKEN` in the source | Pressing reset twice within 10 s |
| [`diy_node_v2/`](diy_node_v2/) | WiFi + token | Portal, stored in NVS | Holding BOOT at power-up |
| `../diy_node_v3/` | WiFi + token + name + site + height | Portal, stored in NVS | A button on the node's own status page, or holding BOOT |

The v1.1 → v2 step is the one that mattered: while the token lived in the source,
every node needed its own build and somebody with the Arduino IDE. From v2 on, one
image serves the whole fleet.

v3 adds no new hardware requirement over v2. If you have v2 nodes in the field they
will keep publishing — the NVS keys are compatible, and a v2 node reflashed with v3
keeps its WiFi and token and simply comes up with the name fields empty.

## Two things to know before reading the source

`diy_node_v1.1.ino` points at `/firmware/v2-bsec2/` for a Bosch BSEC2 revision.
**That folder has never existed in this repo.** The comment was aspirational and is
left in place rather than edited, because these files are kept as a record of what
was flashed.

`diy_node_v2.ino` was called `bayu_sensor_wifimanager.ino` and lived on a laptop
until September 2026. It is committed here unchanged apart from the repository URL
in its header, which pointed at the organisation's old name.
