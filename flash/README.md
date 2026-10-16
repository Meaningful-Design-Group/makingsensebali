# flash/ — the browser flasher

`https://makingsense.fablabbali.com/flash/` puts firmware on a board over a USB cable from Chrome or Edge, with
nothing installed on the laptop. Two targets: the DIY node (v5, XIAO ESP32-S3 and ESP32-C3 SuperMini) and the
Meshtastic radios the PLANETAI nodes use (XIAO ESP32-S3 + Wio-SX1262 flashed from the page; Wio Tracker L1 and
SenseCAP T1000-E as UF2 downloads, because nRF52 boards take a file on a drive, not a serial flash).

## Why it lives here and not on the node

Web Serial exists only in Chromium browsers and only on a secure context: `https://` or `localhost`. A PLANETAI
node's dashboard on the LAN is `http://192.168.x.x:8081` and cannot flash anything. This site is served over
HTTPS, so a workshop of eight laptops can flash from it. The node still owns everything after the flash: region,
frequency slot and channel keys come from the node's QR (`planetai radio url`) or from `planetai radio provision`,
and the DIY node's broker settings come from `planetai broker`. The page sets none of that on purpose.

## Pieces

```
flash/index.html                      the page, in the site's style; strings in flash/i18n-flash.js (en canonical, id and es drafts)
(ESP Web Tools 10.4.0, Apache-2.0, is loaded pinned from unpkg, the CDN the site already uses for Leaflet; the comment in index.html says how to vendor it)
flash/firmware/VERSIONS               the two pins: esp32-core=…, meshtastic=…
flash/firmware/meshtastic/            written by tools/fetch_meshtastic.sh (CI: meshtastic-fetch.yml): the release's files, md5-checked, SHA256SUMS, manifest-xiao-s3.json, files.json
flash/firmware/diy-node/              written by CI (firmware-build.yml): manifest.json and the images per chip, SHA256SUMS
```

The page reads `firmware/diy-node/manifest.json` and `firmware/meshtastic/files.json` at load. When the DIY
manifest is missing (the build has not run yet) the button is hidden and a note says so; nothing else breaks.

## Bumping a version

- **Meshtastic**: change `meshtastic=` in `flash/firmware/VERSIONS` to the stable release tag without the leading
  `v` (the one GitHub does not mark pre-release; alphas are offered first and are not releases). Merge; the
  workflow fetches and commits. Every radio in a mesh must run the same version, so a bump means re-flashing the
  fleet. Old versions stay in the tree until deleted by hand.
- **DIY node**: a push that touches `hardware/diy-node/firmware/diy_node_v5/` rebuilds. The tag in the manifest
  is `FW_VERSION-<short sha>`. The arduino-esp32 core is pinned in `VERSIONS`; libraries are pinned in the
  workflow and recorded in the manifest.

## What a first run will tell you

Neither workflow has run yet (written 16 Oct 2026). `meshtastic-fetch` was exercised locally end to end with the
real release and passes. `firmware-build` was written from the arduino-cli and arduino-esp32 docs; the first run
checks the FQBN option names, the pinned library versions, and whether the core emits a `.merged.bin` (the manifest
falls back to the four-part layout if not). v5 itself has not run on a board as of its own README; flash v5 to one
node and do the bench check in `hardware/diy-node/firmware/README.md` before pointing a workshop at this page.

## Not done, by choice

- No region or channel configuration from the browser. It is possible with `@meshtastic/js` over Web Serial; the
  QR already does it, and the slot pin for Bali is the node's decision.
- No WiFi provisioning from the browser for the DIY node. Improv Serial in v6 would let ESP Web Tools set WiFi
  right after the flash and skip the captive portal; about fifty lines on the Arduino side.
- The service worker (`../sw.js`) only intercepts navigations, so the multi-megabyte images are never cached by it.
