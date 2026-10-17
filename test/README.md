# test/ — the sensor bench

`https://makingsense.fablabbali.com/test/`. Plug a DIY node into USB (Chrome or Edge on a laptop) and each of its
sensors shows working, animated, with a check list: board talking, firmware, sensors found, WiFi, clock, publishing
(and why not: `rc=5` is the broker's user or password). Several boards at once. It reads the lines the firmware
already prints at 115200: v5 `[read]  HM3301 … SEN5x … BME680 …`, v3/v4 `[read] T=… PM2.5=… (bme=1 hm=1)`, and the
test sketch's `[bme680]` / `[hm3301]`. Nothing is reflashed and nothing is sent anywhere.

**Network view and layers.** Served by a PLANETAI node (as `/tester`, once the node carries it), the same file reads
the node's `/health`, `/sensors`, `/readings` and `/nodes` and draws every device the node knows: mesh radios through
the gateway, WiFi pods on its broker, LAN devices, Smart Citizen kits, public stations and models, other nodes. Each
is a layer to turn on and off, plus indoors/outdoors. A browser cannot scan a network or read a node from another
origin, so on this site the network view shows the USB boards only, and says so.

**Offline.** One self-contained file. `sw.js` (scope `/test/` only, so the site's own worker never answers for it)
caches it on the first visit; after that it opens with no internet. Fonts fall back to system faces offline.

**Demo and replay.** Demo plays two Bayu sensors and a small node, every one marked DEMO. Replay plays back a saved
serial log (`.txt`) as if live, for teaching without hardware. Save readings (CSV) is the only way data leaves.

Strings: en canonical, id and es first drafts inside the file (`STR`), sharing the site's `scb-lang` choice.
