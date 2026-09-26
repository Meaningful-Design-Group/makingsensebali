# `data/patterns.json` — what the insight agent publishes

The home page shows a **Pattern** line under the reading when a published pattern lies near the reader. Nothing in this repository computes those patterns. They come from the insight agent, which runs on the Fab Lab Bali node as its own container, next to the vision worker but not inside it.

This file is the contract between the two.

## Why the agent, and why on the node

Public reports are cut to the desa and to the day before they are published, so that no report can point at a house or a daily routine. That is deliberate, and it means the site cannot see time-of-day patterns: "evening burning in Kuta Selatan" only exists in the full-resolution, private data on the node.

So the pattern is found there, by the agent, and only the conclusion leaves: an area, a time window, and counts. Raw reports, exact times, coordinates and photos stay on the node. That is the CARE/PLANETAI rule, applied to one file.

The agent uses a local model only where arithmetic cannot do the job, which is mainly phrasing the summary in three languages. Detection — clustering reports by area, hour and category, and checking whether nearby sensors rose in the same window — is plain computation, and should stay that way so anyone can check it.

## Schema

```json
{
  "generated_at": "2026-09-26T00:00:00Z",
  "patterns": [
    {
      "id": "kuta-selatan-dusk-burning",
      "category": "burning",
      "window": "dusk",
      "hours": "18-20",
      "area": { "desa": "Jimbaran", "kecamatan": "Kuta Selatan", "kabupaten": "Badung" },
      "centroid": { "lat": -8.785, "lng": 115.165 },
      "reports_n": 4,
      "days_n": 10,
      "sensor_rise": true,
      "summary_en": "Evening burning in Jimbaran: 4 reports in 10 days, with nearby sensors rising between 18:00 and 20:00.",
      "summary_id": "Pembakaran sore di Jimbaran: 4 laporan dalam 10 hari, sensor terdekat naik antara pukul 18.00 dan 20.00.",
      "summary_es": "Quemas al anochecer en Jimbaran: 4 reportes en 10 días, con los sensores cercanos subiendo entre las 18:00 y las 20:00."
    }
  ]
}
```

| Field | Required | Notes |
|---|---|---|
| `centroid` | yes | The desa centroid, never a report's own point. The page shows a pattern when this lies within 5 km of the reader (or the selected scale, if larger). |
| `summary_en` | yes | Shown verbatim. `summary_id` and `summary_es` are used when present, English otherwise. |
| `window` | yes | `dawn`, `dusk`, `day` or `night`. |
| `reports_n`, `days_n` | yes | Counts, never names or report IDs. |
| `sensor_rise` | no | `true` only if a sensor within 2 km rose above its own usual for that hour in the same window. |
| `hours` | no | A range of whole hours, WITA. Never an exact minute. |

## Rules the agent must keep

1. **A pattern needs at least three reports on at least three different days.** One angry evening is not a pattern.
2. **Never name a source.** "Evening burning in Jimbaran" is a pattern. "The compound behind the temple" is an accusation, and the data cannot support it.
3. **No area smaller than a desa.** If a cluster only makes sense at a finer scale, it is not published.
4. **Expire.** Drop a pattern when no matching report has arrived for 21 days. The page shows whatever is in the file, so a stale pattern is a false one.
5. **A person reads the summaries before the first publish** in each language, and whenever the agent's prompt changes.

Until the agent runs, the file does not exist. The page treats the 404 as "no patterns" and shows nothing.
