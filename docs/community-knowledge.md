**English** · [Bahasa Indonesia](community-knowledge.id.md)

# What the community has learned

### A working knowledge base on living with air pollution in Bali

*Distilled from ~1,700 messages exchanged between ~218 residents in the Bali Air Dispatch community group, 6 May – 19 August 2026, and published here with the tooling Making Sense Bali contributes to the same problem.*

---

## How to read this

Three kinds of content get mixed together in any community group, and they are **not** equally reliable. This document keeps them apart:

- **Tested** — someone did it, measured it, and reported a result others could reproduce.
- **Reported** — first-hand experience, single source, plausible but unverified.
- **Contested** — disputed within the group, or unsourced. Labelled as such, never presented as consensus.

A fourth thing appears in boxes marked **Campaign tooling**. That is *our* work — the open hardware, the reporting bot, the data layer built by Making Sense Bali at Fab Lab Bali. It is separated out deliberately so you can tell the difference between what a community of residents figured out and what a project is offering. The community findings came first and stand on their own.

**Everything here is anonymous.** No names, phone numbers or addresses. Contributors are referred to only as "a member". Nothing identifies anyone reported as burning.

> **What Making Sense Bali is, in four lines.** A community environmental sensing campaign run by Fab Lab Bali within the Fab City Bali chapter, methodologically descended from the EU Making Sense project and built on the Smart Citizen platform. It contributes three things to the problem described in this document: open-source sensors people can build themselves, a data layer that aggregates them alongside other public networks, and a bot that turns resident observations into a public record. All of it is open — hardware files, code, and data.
>
> It is one participant in a larger ecosystem. **Bali Air Dispatch**, the community group whose knowledge this document collects, is a separate and independent effort. Most of what follows is theirs.

---

## 1. Indoor protection — the most useful thing the community figured out

### Seal first, then filter. This is the headline finding.

The most repeated and most consequential discovery, arrived at independently by several members: **air leaks defeat purifiers, and people massively underestimate their leaks.**

> **Tested.** One member ran *three* high-capacity purifiers on maximum in a bedroom and still couldn't hit target PM2.5. The cause was an unsealed LED lighting trough acting as an air inlet. After sealing it, **a single purifier on a low, quiet setting outperformed the previous three on high.**

A second member independently found the same thing — downstairs rooms held below 5 µg/m³ on low, while a *smaller* upstairs room with three purifiers on high sat around 10× worse. Same cause: unsealed downlights.

**Practical method:**

- Use masking tape to temporarily seal a suspected leak, run overnight, compare readings. Cheap, reversible, diagnostic. Make it permanent only where it works.
- Recessed lighting, downlights and LED troughs are the most commonly missed culprit — check the ceiling, not just doors and windows.
- Silicone or foam weather strips (widely available on Indonesian marketplaces, various profiles) for doors in regular use; tape for doors you never open.
- Walk a portable PM2.5 meter around the house to find where dirty air enters. Members consistently rate this as the highest-value use of a cheap sensor.

### The CO₂ trade-off — the counter-lesson

Sealing works so well that it creates a second problem. This was the group's most productive argument.

- **Tested/reported:** a sealed bedroom with two occupants measured **above 2,000 ppm** overnight. Another member with a partly-open window held **1,000–1,300 ppm with PM2.5 under 10** — offered as a workable middle ground for a small room with three sleepers.
- Reference points cited: outdoor/forest air ≈400 ppm; EU indoor guidance ≈800–1,000 ppm; one member targets 650 ppm.
- **Honest disagreement:** members split on whether 1,800–2,000 ppm actually harms you. One reported no noticeable effect; others report grogginess and headaches. A medically-framed contribution noted that modest CO₂ elevation doesn't cause clinically significant drops in blood oxygen in healthy people — the grogginess is attributed to CO₂ and stale air, not oxygen deprivation.
- **Ventilation guidance offered:** roughly 25–30 m³ per occupant per hour of fresh-air intake with a matching outlet, or about one full room-air exchange per hour.

**The pattern most converged on:** seal tightly → filter hard → ventilate deliberately during daytime hours when outdoor air is acceptable → keep a small controlled opening at night, or accept higher CO₂ on the worst burn nights.

### Two things purifiers do *not* do

- **Purifiers do not remove CO₂ and do not add oxygen.** A clean PM2.5 reading tells you nothing about CO₂.
- **Split-system air conditioning does not bring in fresh air.** It recirculates and dehumidifies. Do not mistake AC for ventilation.

### Choosing a purifier

- **For smoke, the activated carbon bed matters as much as HEPA.** Smoke is gases and VOCs, not only particles. One member's research found most consumer units carry a thin carbon layer, versus 8–12 kg in units built for smoke — but those are largely US brands and **import duty makes them impractical here.** An unresolved gap.
- Locally available units members actually bought and rated: a Japanese-brand unit around IDR 2.5M (quiet, effective, user-cleanable filters, credited by its owner with resolving nasal irritation, though no PM2.5 display); a Chinese-brand "Pro 4" around IDR 3M; a Sharp 84 m² dual-HEPA with activated charcoal; a Philips 900i with onboard PM2.5 display and app scheduling; a Levoit Core 600S.
- **Reported technique:** run purifiers high for an hour or two *before* bed to scrub the room, then drop to sleep mode overnight.
- **Sizing reality check:** a member with a 65 m² high-ceilinged room asked what to buy. The group's answer was consistent — seal the room first, or you'll buy three units to do one unit's job.

> **Campaign tooling — measuring your own room cheaply.**
> The seal-first finding only works if you can measure. The campaign's **DIY Basic node** (Seeed XIAO ESP32-S3 + BME680, **~USD 15–25** in parts, ~2 hours to build in a workshop) reads temperature, humidity, barometric pressure and a gas/VOC indicator, and publishes to the Smart Citizen platform. It is designed exactly for the indoor case: is my bedroom in mould-favourable conditions, is there a VOC source, did sealing that ceiling gap change anything.
> **Be clear about what it does not do:** it has **no PM2.5 sensor** (that's the Plus tier below) and **no CO₂ sensor** — the BME680's gas reading is a VOC indicator, not CO₂, and the on-device IAQ index is a relative approximation, not a calibrated figure. For the CO₂ trade-off discussed above you need a real NDIR CO₂ sensor, which this is not.
> Build files, firmware and printable enclosure: [`hardware/diy-node/`](../hardware/diy-node/). Print the enclosure in **PETG, not PLA** — PLA softens at Bali rooftop temperatures.

### Whole-house and ducted approaches (advanced, not yet validated)

An active thread on filtered fresh-air intake — HEPA 13/14 plus activated carbon on an inline duct fan, sized 200–500 m³/h, to solve PM2.5 and CO₂ at once. Indonesian inline duct and HEPA suppliers were identified (6", 8", 10" pipe feeds), along with ultra-thin duct fans with integrated HEPA. **Status: specified, not yet reported as installed and measured.** The most promising unfinished thread in the group.

---

## 2. Masks and personal protection

### Half-face respirators are the community's power-user answer

**Tested** by multiple members. Working configurations:

| Setup | Use case | Notes |
|---|---|---|
| 3M 6200 or 6502 body + 2091 / 2097 / 2093 P100 filters | Motorbike — **fits under a full-face helmet** | 6200 is slimmer; 6502 slightly bulkier, softer silicone, more comfortable |
| 3M 7503 + 7093 P100 | Around the house when pollution is bad | Most comfortable for long wear; too bulky for a helmet |

These are industrial respirators certified for particulate protection. They don't get soggy like paper masks and are comfortable enough for extended wear. The 2097-type filters add a carbon layer for organic vapour and nuisance odour, which is relevant for smoke.

> ⚠️ **Counterfeit warning — the most important safety note here.** Fake 3M products are widespread on Indonesian marketplaces. A member deliberately bought both genuine and fake units to compare. Conclusion: you *might* get away with a counterfeit mask body, though material quality is worse, but **buy filters only from the official 3M store** — the filter is the part that protects you. Official-store prices were found to differ between marketplaces, so it is worth comparing.

### Motorbike-specific premium option

A French-made anti-pollution motorbike mask is resold locally at roughly **IDR 1.9M including filter**, one size, with reports of 14-year-olds wearing it successfully. A member who used it daily for two weeks reported it as genuinely more breathable than N95s, snug with two adjustable straps, with a fit consideration under a closed full-face helmet.

> **Disclosure:** the reseller of this mask is an active member of the group. Their promotional descriptions use phrases such as "military-grade filtration," which is a marketing term and not a technical certification — treat it accordingly. The independent user review above is the more useful signal. Listed here because members found it genuinely useful, not as an endorsement.

### Masks for children — fit beats rating

**Consensus:** the binding constraint for children is **seal, not filtration class**. A well-fitting KF94 or KN95 sized for a child will outperform a poorly-fitting adult N95. Parents also reported buying pharmacy-brand children's masks locally.

Sourcing tip: search Indonesian marketplaces under the category **APD** (*alat pelindung diri*) rather than English terms.

---

## 3. Monitoring — what to buy, and how much to believe it

### The network standard

**AirGradient** emerged as the group's consensus platform for contributing to the shared network — outdoor Open Air O-1PST and indoor ONE I-9PSL, assembled or as kits. The kit saves roughly USD 100 and needs no soldering: "clicking a few cables in and a few screws." There is a mobile app and a public map.

**Import experience, documented by a member so others wouldn't have to guess:**

- Ships from Thailand, about 2.5 weeks door to door.
- **IDR 667k total customs and tax for two units** (one indoor kit + one outdoor kit).
- The vendor later enabled **DDP with customs prepaid at 19.2%**, removing the surprise.
- Process was smooth: the courier emails a bank account and amount on delivery day.

**A step often missed:** after connecting a monitor you must **opt in to sharing outdoor readings** with the public map and OpenAQ. A sensor that isn't opted in is invisible to everyone else.

> **Campaign tooling — the affordable density layer, and what it costs you in accuracy.**
> The campaign builds an open-source **DIY node** in two tiers, designed to be assembled in a Fab Lab Bali workshop by people with no electronics background:
>
> | Tier | Parts | Cost | Measures |
> |---|---|---|---|
> | **Basic** | XIAO ESP32-S3 + BME680 | **~USD 15–25** | Temperature, humidity, pressure, gas/VOC indicator |
> | **Plus** | Basic + Seeed Grove HM3301 | **~USD 35–60** | Adds PM1 / PM2.5 / PM10 |
>
> Same firmware runs both. Roughly 2 hours to build Basic, 3 hours for Plus, from kit to live on the dashboard. Everything is open: firmware, parametric enclosure, STLs, schematic, BOM with Indonesian sourcing notes.
>
> **The honest positioning.** This is *not* a cheaper replacement for an AirGradient or an official Smart Citizen Kit (~USD 150). Those are the trusted backbone — calibrated, drift-compensated, battle-tested. The DIY node buys **spatial density per campaign rupiah**: for the price of one official kit you can put 3–4 Plus nodes or 6–10 Basics into kos rooms, schools, warungs and banjar compounds. Density is the point, not accuracy.
>
> **What you give up:** no noise sensor, no eCO₂, no calibrated or drift-compensated readings, and **PM sensor drift in tropical humidity is real**. When campaign data includes DIY-node readings they are marked as such on the dashboard, with lower stated fidelity. Mixing tiers silently would be dishonest and would undermine exactly the credibility this data needs to carry into a government conversation.
>
> **Sourcing warnings for Bali, learned the hard way:** verify the IC marking actually reads **BME680** — sellers mislabel BME280 and BMP280, and only the BME680 has the gas sensor. The HM3301 is the cost driver; for 5+ kits, ordering direct beats local retail markup, but budget three weeks.
>
> Files: [`hardware/diy-node/`](../hardware/diy-node/)

### How much to trust a cheap sensor

Where the community's collective testing is genuinely valuable:

- **Tested:** two units of one popular cheap handheld brand read **1.5–1.6× higher** than nearby calibrated sensors. Consistently — which makes the bias usable if you know about it.
- **Tested:** a 3× discrepancy between a purifier's onboard sensor (~30 µg/m³) and an AirGradient (~10 µg/m³) in the same room. Explanation offered: placement, plus different **calibration and humidity-correction algorithms**. AirGradient exposes both **raw and corrected** values via its local API — comparing raw against the other device isolates how much of the gap is correction rather than hardware.
- **The right mental model:** cheap portables are excellent for *relative* comparison — finding leaks, comparing rooms, proving a purifier works, walking around to locate a source. They are unreliable for *absolute* numbers. Fixed, calibrated, always-on outdoor sensors are what make a network credible.

### Reading a public map critically

Members noticed neighbouring sensors reporting wildly different values (67 vs 9 µg/m³ in the same area) and correctly diagnosed the likely cause: **some "outdoor" sensors are physically indoors**, often inside a filtered space. Worth knowing before drawing conclusions from any single station.

**Interpretation guidance that emerged:** one sensor spiking while its neighbours stay flat indicates a very local source. Several sensors rising and falling together is much stronger evidence of a genuine area-wide event. **Geographic coverage matters more than total sensor count** — a sensor filling a gap is worth more than another in a well-covered area.

> **Campaign tooling — where the readings go.**
> Campaign sensors publish to the **[Smart Citizen platform](https://smartcitizen.me/)**, an open platform for citizen-operated environmental sensing (co-founded at Fab Lab Barcelona in 2012). The campaign's data layer then aggregates Smart Citizen alongside **OpenAQ**, **Sensor.Community**, **AirGradient** and **PurpleAir** into one public dashboard, so devices from different networks appear together with their source and last reading shown. If you already run a sensor on any of those networks, it can be pulled in without you changing anything — the DIY node is only one path in.
> Data is published openly under CC BY 4.0. The campaign also carries a Murmurations profile so the dataset is discoverable across federated community-data networks.

### 🔴 Still open: no calibration reference

Asked twice in the group, never resolved: **where in Bali can anyone check a monitor against a reference-grade instrument?** Members proposed testing at both high and low concentrations to establish whether device error is a constant offset or a linear scaling factor. Nobody identified a facility.

This is the highest-leverage unsolved technical problem here, and it is not one the campaign can solve alone — it needs an institution with a reference instrument, plausibly the meteorological agency or a university. It matters more, not less, as cheap sensors proliferate: the DIY node's humidity drift and every handheld's bias are all guesses until something authoritative exists to check them against.

---

## 4. Understanding the pollution itself

### Timing — the community's observational epidemiology

Independently corroborated by many members across different areas:

- **Twice-daily household burning at sunrise and sunset.** In some neighbourhoods this is social — everyone out at the same time with metal bins, chatting while they burn.
- **A distinct morning peak roughly 07:00–09:00**, with air improving through the day.
- **Night burning from about 01:00–03:30**, reported as the worst and hardest to locate. One member drove around at night trying to find the source and couldn't, describing an entire village blanketed in smoke.
- **Spikes after ceremonial days**, as accumulated waste is cleared.
- **Rice-field stubble burning** as a seasonal agricultural layer on top of household burning.
- **Still air is the multiplier.** With no wind the smoke simply hangs over the village — the same burn is far worse on a calm night.

### The structural cause, stated plainly by the group

The clearest-eyed thread in the archive. Members converged on a diagnosis that is uncomfortable and probably correct:

1. **Burning is a symptom of missing waste collection, not primarily of ignorance.** A family burning daily was found to have no rubbish pickup at all and years of accumulated backlog.
2. **The Suwung landfill closure removed the alternative.** Collection services, including established recycling operators, refused new customers because they were full. A member in the Tabanan area asked publicly for *any* working collection option and got no solution.
3. **Enforcement is therefore hollow.** Burning non-organic waste is illegal and people know it. But when a member contacted local security about a facility burning plastic, they were told to go speak to the facility themselves.
4. **A local perspective relayed in the group:** nobody wants to report anyone else's harmful practice, because they are themselves doing something reportable. Tragedy of the commons.

**The operational implication:** telling someone burning is harmful, without offering a functioning alternative, does not work and can damage the relationship. Pair every ask with a solution.

### Sources beyond household burning

- **Waste facilities and small incinerators** were flagged repeatedly and several were mapped by members. One reported fumes carried about 450 m on easterly winds every afternoon. Members raised a serious question: a new middle school was reportedly built beside one such facility, and there appears to be **no monitoring at any of them**.
- The provincial **waste-to-energy project** — members translated and circulated Indonesian reporting on comparable plants in East and Central Java that failed, as a caution against assuming a new facility solves this.

### 🔴 Still open: dioxins and furans

Asked early in the group, never answered, so let us answer it plainly here: **no, these monitors do not detect dioxins and furans.** PM2.5 and VOC sensors do not speciate. Since burning plastic is the central concern and dioxins are among its most serious hazards, the honest position is that **every network described in this document — ours included — measures a proxy, not the most toxic component of the smoke.** Proper dioxin measurement requires laboratory sampling and is outside the reach of citizen sensing as it currently exists in Bali.

> **Campaign tooling — what a sensor cannot see.**
> A sensor records that PM2.5 spiked at 06:40. It cannot record that it was a household burn two doors down, that it happens every morning, or what was on the fire. That gap is why the campaign runs a **reporting bot** alongside the sensors.
> Residents send an observation — category, photo, location, rough time — through **WhatsApp, Telegram, or an anonymous web form**, in English, Bahasa Indonesia or Spanish. Every report is reviewed by a human moderator before anything is published. The result is a qualitative record that sits alongside the quantitative one: sensors establish *that* and *how much*, reports establish *what* and *why*.
> The timing patterns the community documented above are exactly the kind of claim this record can eventually corroborate or correct with evidence rather than impression.

---

## 5. The escalation ladder — how to actually get burning to stop

The most valuable and least documented knowledge in the archive: hard-won social protocol.

### The sequence that reflects local norms

1. **Neighbour to neighbour, first.** Explained by a member with local knowledge: in Balinese villages the expectation is that neighbours try to resolve things together before escalating. Going over someone's head first damages the outcome.
2. **Then the banjar / klian.** Reported as effective — *"They have authority and respect, and people listen to them."* One member found the banjar responsive and supportive where direct appeals to individuals had been dismissed. Introduce yourself properly, build the relationship, then ask for help.
3. **Then the environmental agency — the level-skip that worked.** One of the most useful single data points here: a member reported an issue to their village head and **nothing happened**; they then went **directly to the environmental agency, who arrived the next day and resolved it** — and told the village head it should never have escalated that far. (That case was noise, but the path is the transferable insight.)
4. **Local security (linmas):** tried, produced only a redirection. Least effective route reported.

### What actually persuaded people

**Tested, with a documented success.** One member's account of ending daily burning by an extended family of about 20:

- They **met the family in person** rather than reporting them.
- They found the real constraint: no rubbish collection, years of backlog dumped in a back plot, and **the banjar had never talked to them about composting**.
- They treated it as a **shared problem**, proposing a composting system and framing the family as potentially **the first in the village with a good system**, with the klian invited to see it once working.
- Result the next day: *"First morning waking up without smoke."*
- Their own framing of why it's worth it for one household: it creates **a template to share with the rest of the village.**

**Other tactics members reported working:**

- **Show the live reading on your phone.** Several described the moment a neighbour sees the number turn red as the thing that lands. Abstract harm doesn't; a colour does.
- **Lead with children's health.** Consistently the most persuasive frame.
- **A member produced a printed explainer for exactly this** — health impacts for children, adults and elderly, then solutions. Community-made and reusable.

**What didn't work:** telling people it's bad with nothing to offer. One member described being met with smiles and blank stares and feeling "useless."

> **Campaign tooling — evidence, and the option not to be identified.**
> Two things in the reporting system are aimed directly at the problems in this section.
>
> **A record you can take to a banjar.** "I think they burn most mornings" is an opinion. A set of timestamped, photo-backed, moderated reports is evidence. The campaign keeps the full detail — precise location, exact time, original photographs — privately, and can prepare a **dossier for a specific area on request**, for someone approaching a klian banjar or a regency office. That material is produced deliberately for a named recipient. It is never a public endpoint.
>
> **Anonymous reporting, because several members said plainly that they are afraid to speak up.** The web form requires no account, no phone number and no name. Nothing links a report to a person. On Telegram the bot sees a chat ID, never a phone number. On WhatsApp the number is used only to reply and is then stored as a keyed, salted code.
>
> **And what gets published is deliberately blunt.** Reports appear at **desa/kelurahan level with day-only dates** — never exact coordinates, never a time of day. This is a direct response to a concern raised by members of this very community: that a map of precise, repeated burning locations becomes a public directory of which household is responsible. It would also endanger reporters. The public layer is built to show *that a problem exists and where it concentrates*, and nothing more. Precise data exists, is retained, and stays private.

---

## 6. Fixing the source — waste-side solutions

- **Home composting with compost bags — the most accessible win in this document.** Around **IDR 60k** each, available online. **Tested by at least three members**, one for over two years. The technique repeatedly shared: **interlace waste with layers of soil to prevent smell.** Buy a little soil to start. One member noted animal bones go in a designated spot near the road where local animals clear them immediately.
- **A composting initiative for family compounds** — leaves and food scraps in, fertile soil out, instead of burning sweepings.
- **A local organic-waste processing business**, founded by a school parent in the group, taking organic waste that would otherwise be incinerated. The founder was notably modest about scale.
- **Batteries and household hazardous waste** — asked, and answered: Badung has a **B3 facility in Mengwitani** receiving household hazardous waste including used batteries via the TPS3R and *bank sampah* network, forwarding to licensed processors. A concrete answer to a real disposal gap.
- **Pyrolysis** was raised as a way to convert plastic into fuel and wax, with a claimed large emissions reduction versus open burning. ⚠️ **Contested and unsourced.** No study was provided, DIY pyrolysis carries real fire, toxicity and emissions risks, and the claim is not repeated here as a figure. Recorded only as an idea in circulation. **Not a recommendation.**
- **School programmes work, and there is a local precedent.** A member described a project in Bondalem, Buleleng: a small truck able to reach narrow lanes, teacher training, and two-hour Saturday sessions for children aged 8–12 on recycling, waste separation and growing plants in composted soil. Adopted and sustained. The strategic response it drew from another member: **a short documentary in Bahasa would spread this faster and more cheaply than anything else.**

---

## 7. Collective infrastructure and advocacy

- **Petition method.** A member who had run a successful local petition advised: state the problem *with evidence*, identify who can act, and specify what you're asking for. Vague petitions fail.
- **A cautionary precedent that shaped this project's design.** A commercial Indonesian air-monitoring network shut down its sensors, reportedly over funding. **A network that depends on one company's business model can vanish, taking the historical record with it.**
- **Institutional threads in progress:** an MOU with a Bali health organisation, and conversations about placing monitors in villages with Indonesian-language communication support. The recurring insight: **the communication layer has to be Indonesian-led to land.**
- **A civic toolkit from a prior participatory noise-monitoring campaign in Barcelona** was shared as a template for structuring a Bali air-quality campaign.
- **Drone-based fire-finding — an active thread.** Night burns are nearly impossible to locate from the ground. Proposals: a thermal-imaging enterprise drone with a retrofitted PM2.5 sensor; or far cheaper, a consumer drone with SDK access flying autonomous grids, images assembled into orthophoto maps with open-source tooling. Practical notes: 25–30 min flight time on higher-capacity batteries, wind is the limiting factor, and older drone models have better third-party software support because manufacturers release SDKs only after some years.
- **Satellite fire maps** were used by members to place Bali's burning in a global context.

> **Campaign tooling — why this one is built to outlive its funding.**
> The shutdown described above is the argument for how Making Sense Bali is constructed. The hardware is open source, so anyone can build or fork it. The data is published openly under CC BY 4.0 as static files, so it survives any single organisation. The sensors publish to Smart Citizen and federate to OpenAQ, so the readings exist in more than one place. The campaign carries a Murmurations profile so the dataset stays discoverable independently of any platform. There is no company here to withdraw a service.
> This is a design stance, not a claim of permanence — an open network can still be abandoned. But it cannot be switched off by one party, and everything needed to restart it is public.

---

## 8. Myth-busting — where the community corrected itself

**Houseplants do not solve CO₂.** A genuinely useful disagreement. One member cited a peer-reviewed paper suggesting two snake plants meaningfully reduced closed-room CO₂. Others pushed back with an order-of-magnitude argument: a sleeping human produces hundreds of litres of CO₂ daily; snake plants are CAM plants and do absorb some at night, but the amounts are trivial by comparison. The widely-circulated "6–8 snake plants can keep you alive in a sealed room" claim is a **misquotation of old NASA research that has been explicitly debunked.**

**Status: unresolved in-group, with the weight of argument favouring ventilation.** A member offered to test it directly once they have a CO₂ sensor — the right response, and a small experiment this community could actually run and publish.

**"I close my windows when I burn."** Recorded because it captures the core misconception the work is up against: several members met neighbours who genuinely believe closing their own windows makes their burning harmless to everyone else.

---

## 9. Open needs — where this community is stuck

Unanswered questions with real demand behind them. Each is a candidate for a project, a partnership, or a workshop.

| Need | Status |
|---|---|
| A calibration reference for citizen sensors in Bali | Asked twice, no answer. Highest-leverage technical gap. Needs an institution with a reference instrument. |
| Working waste collection in Tabanan / Tanah Lot / Seseh | Multiple requests, services full, no solution found. The structural blocker behind most burning. |
| Dioxin and furan measurement | Beyond citizen sensing as it stands. Requires lab sampling. Until then, every network here measures a proxy. |
| Monitoring at waste facilities and small incinerators | Raised with mapped locations; no monitors installed. A concrete deployment opportunity. |
| An affordable heavy-activated-carbon purifier available in Indonesia | Identified as the right tool for smoke; import cost blocks it. Possible local-manufacture project. |
| The neighbour explainer, properly published in Bahasa | Exists as a community artifact; deserves a permanent home rather than scrolling away in a chat. |
| A Bahasa video documenting the Bondalem school programme | Explicitly requested in-group as the fastest way to spread a model that already worked. |
| Whole-house filtered fresh-air intake, built and measured | Specified in detail; no completed installation reported. |
| Sensor coverage in under-covered areas | Geographic gaps are worth more than density in covered areas. The DIY node exists to lower this barrier — [`hardware/diy-node/`](../hardware/diy-node/). |

---

## Contributing, and a note on what this is

If you are in the Bali Air Dispatch group and something here is wrong, incomplete, or attributed to the wrong kind of confidence, it should be corrected — open an issue or a pull request on this repository, or say so in the group.

If you have a sensor already running on AirGradient, PurpleAir, Sensor.Community or Smart Citizen, opting in to public data sharing adds it to the shared picture at no cost to you. If you want to build one, the files are in this repository. If you want to report something a sensor cannot see, the reporting bot exists for that.

**A caveat on health information.** The symptom accounts in this document are community reports, not clinical evidence. Persistent cough, breathing difficulty or other ongoing respiratory symptoms warrant seeing a doctor — this document is not medical advice.

**A caveat on the products named.** Nothing here is a paid placement or an endorsement. Products appear because members bought them and reported back. Where a member has a commercial interest, it is stated.

---

*Community knowledge collected from the Bali Air Dispatch group, 6 May – 19 August 2026, and published by Making Sense Bali at Fab Lab Bali, within the Fab City Bali chapter. The community findings belong to the people who produced them. Contributions are anonymous by design.*
