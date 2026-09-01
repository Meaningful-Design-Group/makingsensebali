**English** · [Bahasa Indonesia](CONTRIBUTING.id.md) · [Español](CONTRIBUTING.es.md)

# Contributing to Making Sense Bali

This is a community-led environmental sensing campaign for Bali, anchored by
[Fab Lab Bali](https://fablabbali.com). Sensors, resident reports, and the
tooling that connects them.

You do not need to be a programmer to contribute, and you do not need
permission to start. Open an issue, or open a pull request.

## One rule before anything else: never publish a person

This repository handles reports from residents, some of whom have said plainly
that they are afraid to speak up about burning near their homes. Anonymity is
not a nice-to-have here — it is the reason people participate at all.

So, in any issue, pull request, screenshot, log paste or test fixture:

- **No phone numbers, names, WhatsApp handles or chat IDs.**
- **No exact coordinates of a report.** Published reports are deliberately
  snapped to the centroid of a desa. Do not undo that, and do not paste
  precise coordinates from private data into a public issue.
- **No original photographs from reports.** Published photos have had EXIF
  stripped; originals stay private.
- **No timestamps to the minute** on individual reports. A precise time on a
  repeated report identifies a person with a routine.

If you find any of the above already published somewhere in this repo, that is
a security issue, not a bug — email tomas@fab.city rather than opening a
public issue.

## What is useful

**Hardware.** Enclosure designs, sensor node variants, field fixes. The rule
is *source and export, always*: a `.step` or `.scad` alongside the `.stl`, so
the next lab can modify rather than only print. Export-only contributions will
be accepted but flagged as incomplete. Start in
`hardware/diy-node/enclosure/` — the current design is `bayu-v6/`, and
`previous-iterations/` explains what each retired design got wrong.

**Firmware and tooling.** `hardware/diy-node/firmware/`, `tools/`, `worker/`.
Smart Citizen integration notes live in `docs/`. If you are adding a sensor
channel, read the data-honesty rules first: no fake zeros, no NaN, average
rather than sample. A failed reading must contribute nothing, because on a
dashboard `PM = 0` is indistinguishable from clean air.

**Translations.** Everything ships in English, Bahasa Indonesia and Spanish.
English is canonical; the other two are translations. Strings live in
`i18n.js` — add a key to all three dictionaries or the site falls back
silently. Bahasa quality matters most: this site serves Balinese residents
first.

**Community knowledge.** [`docs/community-knowledge.md`](docs/community-knowledge.md)
is distilled from the [Bali Air Dispatch](https://baliairdispatch.com/)
community group. If something there is wrong, incomplete, or stated with more
confidence than the evidence supports, correcting it is a real contribution.

**Replication.** If you build a node, or fork this as *Making Sense [your
city]*, tell us. What you had to change to source parts locally is more useful
to the next lab than anything we can write from here.

**Reporting.** The lowest-effort contribution and the one the campaign runs
on: [report what you see](https://bali-aq.fab.city/report). Anonymous, no
account, no phone number.

## How to submit

1. Fork, branch from `main`. Name it for what it does —
   `hardware/…`, `docs/…`, `fix/…`.
2. Keep pull requests to one concern. A PR that fixes a bug *and* reorganises
   a folder is two PRs.
3. Describe what you changed and, for hardware, what you tested it against.
   "Printed and deployed for three weeks in Denpasar" is worth more than a
   render.
4. Bahasa or Spanish are fine in issues and PR descriptions. Code comments in
   English, so the widest set of contributors can read them.

There is no CLA. By contributing you agree your work is released under the
licences below.

## Licences

| What | Licence |
|---|---|
| Software — firmware, tooling, site | MIT |
| Hardware — CAD, STL, mechanical design | CERN-OHL-W-2.0 |
| Documentation, images, community knowledge | CC-BY-SA-4.0 |
| Published report data | CC-BY-4.0 |

CERN-OHL-W is weakly reciprocal: a workshop can build and sell nodes
commercially, and improvements to the design come back.

## Repository map

```
hardware/diy-node/     enclosures (bayu-v6 is current), firmware, tools
dashboard/             live sensor dashboard
docs/                  methodology, community knowledge, platform notes
reports/               the reports pipeline and moderation dashboard
worker/                Cloudflare worker proxying OpenAQ
data/                  published, moderated report data — machine-written
i18n.js                all site strings, three languages
```

`data/` is written by an automated sync. Don't edit it by hand.

## Contact

Tomas Diez — tomas@fab.city. For anything touching a person's identity or
safety, email rather than opening an issue.
