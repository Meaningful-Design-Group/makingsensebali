#!/usr/bin/env bash
# Pin one Meshtastic release for the flash page. Downloads the esp32s3 and nrf52840 release zips, takes the five
# files the page serves, checks each against the md5 in the release's own .mt.json, writes
# flash/firmware/meshtastic/<version>/, files.json, manifest-xiao-s3.json and SHA256SUMS. Idempotent.
#
#   tools/fetch_meshtastic.sh 2.7.26.54e0d8d
#
# Which version: the stable release (the one GitHub does not mark pre-release). docs/MESHTASTIC.md in planetai-node
# says why: the web flasher offered a 2.8.1 alpha first. Every radio in a mesh runs the same version; bumping this
# means re-flashing all of them, so it is a decision, not a refresh. The version in use is in flash/firmware/VERSIONS.
set -euo pipefail
VER="${1:?version, e.g. 2.7.26.54e0d8d}"
cd "$(dirname "${BASH_SOURCE[0]}")/.."
OUT="flash/firmware/meshtastic"; DIR="$OUT/$VER"; TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
REL="https://github.com/meshtastic/firmware/releases/download/v$VER"
say() { printf '\033[1;32m>>\033[0m %s\n' "$*"; }
die() { printf '\033[1;31mxx %s\033[0m\n' "$*" >&2; exit 1; }

say "fetching the esp32s3 and nrf52840 zips for $VER"
for plat in esp32s3 nrf52840; do
  curl -sSfL --retry 3 -o "$TMP/$plat.zip" "$REL/firmware-$plat-$VER.zip" || die "no firmware-$plat-$VER.zip at $REL (is $VER a real tag, without the leading v?)"
done
mkdir -p "$DIR"
unzip -o -q "$TMP/esp32s3.zip"  "firmware-seeed-xiao-s3-$VER.factory.bin" "firmware-seeed-xiao-s3-$VER.mt.json" -d "$TMP/s3"
unzip -o -q "$TMP/nrf52840.zip" "firmware-seeed_wio_tracker_L1-$VER.uf2" "firmware-seeed_wio_tracker_L1-$VER-ota.zip" "firmware-seeed_wio_tracker_L1-$VER.mt.json" \
                                "firmware-tracker-t1000-e-$VER.uf2" "firmware-tracker-t1000-e-$VER-ota.zip" "firmware-tracker-t1000-e-$VER.mt.json" -d "$TMP/nrf"

# the release's own manifest carries an md5 per file; refuse a file that does not match it
check() { # <mt.json> <file>
  local want; want="$(python3 -c "import json,sys; print(next(f['md5'] for f in json.load(open(sys.argv[1]))['files'] if f['name']==sys.argv[2]))" "$1" "$(basename "$2")" 2>/dev/null || true)"
  [[ -n "$want" ]] || { say "   (no md5 listed for $(basename "$2"); kept, hashed below)"; return 0; }
  local got; got="$(python3 -c "import hashlib,sys; print(hashlib.md5(open(sys.argv[1],'rb').read()).hexdigest())" "$2")"
  [[ "$want" == "$got" ]] || die "$(basename "$2"): md5 $got, release says $want"
}
check "$TMP/s3/firmware-seeed-xiao-s3-$VER.mt.json" "$TMP/s3/firmware-seeed-xiao-s3-$VER.factory.bin"
for b in seeed_wio_tracker_L1 tracker-t1000-e; do
  check "$TMP/nrf/firmware-$b-$VER.mt.json" "$TMP/nrf/firmware-$b-$VER.uf2"
done
cp "$TMP"/s3/* "$TMP"/nrf/* "$DIR/"
say "files match the release's md5s"

cat > "$OUT/manifest-xiao-s3.json" <<J
{
  "name": "Meshtastic · Seeed XIAO ESP32-S3 + Wio-SX1262",
  "version": "$VER",
  "new_install_prompt_erase": true,
  "builds": [
    { "chipFamily": "ESP32-S3", "parts": [ { "path": "$VER/firmware-seeed-xiao-s3-$VER.factory.bin", "offset": 0 } ] }
  ]
}
J
cat > "$OUT/files.json" <<J
{
  "version": "$VER",
  "channel": "stable",
  "xiao_s3_factory": "firmware-seeed-xiao-s3-$VER.factory.bin",
  "tracker_l1_uf2": "firmware-seeed_wio_tracker_L1-$VER.uf2",
  "tracker_l1_ota": "firmware-seeed_wio_tracker_L1-$VER-ota.zip",
  "t1000e_uf2": "firmware-tracker-t1000-e-$VER.uf2",
  "t1000e_ota": "firmware-tracker-t1000-e-$VER-ota.zip"
}
J
( cd "$DIR" && sha256sum -- *.bin *.uf2 *.zip > SHA256SUMS )
grep -q "^meshtastic=" flash/firmware/VERSIONS 2>/dev/null && sed -i.bak "s/^meshtastic=.*/meshtastic=$VER/" flash/firmware/VERSIONS && rm -f flash/firmware/VERSIONS.bak || echo "meshtastic=$VER" >> flash/firmware/VERSIONS
say "wrote $DIR ($(du -sh "$DIR" | cut -f1)), manifest-xiao-s3.json, files.json. Old versions are not removed: delete them by hand when every radio has moved."
