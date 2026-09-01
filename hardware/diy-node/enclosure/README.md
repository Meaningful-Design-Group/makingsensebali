# Enclosures

**Current design: [Bayu Sensor Enclosure v6](bayu-v6/).** Build that one.

Everything else lives in [`previous-iterations/`](previous-iterations/) and
is kept for its failure notes, not for building.

| | |
|---|---|
| [`bayu-v6/`](bayu-v6/) | Canonical. Six printed parts, STLs published, CAD source still missing. |
| [`previous-iterations/`](previous-iterations/) | Node V2, v5 pine cone, v1–v4. Retired, documented. |
| [`LICENSES/`](LICENSES/) | CERN-OHL-W-2.0 hardware · CC-BY-SA-4.0 docs · MIT software |

---

## Landing this in the repo

This folder is a drop-in for `hardware/diy-node/enclosure/` in
`Meaningful-Design-Group/makingsensebali`. Do it on a branch — the existing
enclosure content needs to move rather than be overwritten, and `git mv`
keeps the history attached to the files.

```bash
git clone https://github.com/Meaningful-Design-Group/makingsensebali --depth 1
cd makingsensebali
git checkout -b hardware/bayu-v6-canonical

cd hardware/diy-node/enclosure
mkdir -p previous-iterations

# move, don't copy — history follows the files
git mv archive previous-iterations/
git mv enclosure.scad stl img ref_hm3301_board.pdf previous-iterations/
git mv README.md README.id.md README.es.md previous-iterations/

# the Node V2 track moves in too
cd ../..
git mv hardware/diy-node/node-v2 hardware/diy-node/enclosure/previous-iterations/node-v2
```

Then copy this folder's contents over `hardware/diy-node/enclosure/`,
merging `previous-iterations/README.md` with whatever the moved READMEs say.

### Bring the V2 CAD in from the standalone repo

`Meaningful-Design-Group/Enclosure-DIY-Node-V2` contains exactly one file —
`Enclosure DIY Node V2.f3z`, 6.8MB, no README, no licence, untouched since
3 July. That file is the answer to the Node V2 docs' own blocking TODO:
*"Enclosure CAD source and STL are not in the repo — only in a Google Drive
folder."*

```bash
git clone https://github.com/Meaningful-Design-Group/Enclosure-DIY-Node-V2 /tmp/v2cad
mkdir -p hardware/diy-node/enclosure/previous-iterations/node-v2/cad
cp "/tmp/v2cad/Enclosure DIY Node V2.f3z" \
   hardware/diy-node/enclosure/previous-iterations/node-v2/cad/
```

Then archive the standalone repo with its description pointing here. One
public home per design.

### Fetch the licence texts

See [`LICENSES/README.md`](LICENSES/README.md) — two `curl` commands. Don't
transcribe them by hand.

---

## Before this is replication-ready

Ordered by what blocks reuse, not by effort:

1. **Publish the CAD source for Bayu v6.** STL-only means nobody can modify
   it. `.step` alongside the native file is the minimum.
2. **Re-export `Main_Body.stl`** — it has 4 open edges and is not watertight.
3. **Print settings** — material first. PLA will not survive a tropical
   roof.
4. **BoM** — screw sizes and counts, at minimum.
5. **Assembly steps and photos.**
6. **State how v6 answers the two failures** (self-heating, intake lag) in
   the Bayu README. One paragraph. Nobody else can write it.

Items 1 and 2 are the ones that determine whether another Fab Lab can
actually build this or is just looking at pictures of it.
