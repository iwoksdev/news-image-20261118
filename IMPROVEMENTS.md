# IMPROVEMENTS.md — how to climb from #174

Current: **rank 174 / 7,347, judge win rate 98.39%**. Rank 1 is 99.10%.
The judge is pairwise; scores are compressed at the top, so small quality
gains move many places. Work top-down: do item 1 first, then 2, and so on.
One item per commit (see AGENTS.md).

## Study the top entries first

Fetch any top entry's judged image (WebP) and look at it next to ours:

```
GET https://make.fun/api/submissions/<submission_id>/artifact.webp
```

| Rank | Handle | Submission | Judge | Title |
|---|---|---|---|---|
| 1 | el-net | `01a1ee39-409b-7223-8523-b644dac9b52f` | 99.10% | Gulf drone strikes, Trump–Xi–Putin eve, 43 more stories |
| 2 | tri-le | `01a1ef7b-036f-7313-8be8-0e13bf1b4ac9` | 99.07% | Xi greets Trump at APEC, Iran's drones at Kuwait, COP31 split, 35 more |
| 3 | yoshifumi-nagata | `01a1eef9-d36d-7720-b365-1946b9132cdf` | 99.02% | The day's world news on one front page |
| 4 | calm-badger-15 | `01a1ecc7-364d-7543-bd10-40006b18bda9` | 99.00% | 35 stories, 6 continents, one front page |
| 5 | poorya0128 | `01a1f003-7dab-7174-8422-61c72822b023` | 98.98% | The World in a Day |
| 6 | awsm13 | `01a1ef1d-7c40-744e-929c-17df2c08e8d2` | 98.97% | 30 stories, 6 continents, one front page |

Ask: what do the top 5 do that ours doesn't? (Denser story count? Cleaner
hero art? More readable type? Better map?) Copy the mechanism, never the
image — do not trace or reuse their pixels.

Live standings (updates as entries arrive):
`GET https://make.fun/api/competitions/news-image-20261118/leaderboard`

## Ranked ideas

### 1. Fix the weakest hero art (highest value)
Hero 1's plane renders as a white blob — redraw it as a clean, recognizable
Air Force One / tarmac scene. The Voyager panel and the Gulf map are already
good; bring hero 1 up to their level. Check the top entries' hero panels for
what "clean" looks like at 1024px.

### 2. Verify-or-replace the unverified items
These were never independently verified — they were carried over from the
reference image. Verify each with a live source; replace or drop what you
cannot confirm (do not invent):
- "Russia fires 141 drones, 126 downed" (count + Odesa casualties)
- "Cyclone Akvan" (name + landfall timing)
- "Ethiopia and Eritrea mass troops on the border"
- "GTA VI unlocks first in New Zealand … from 11:00 GMT"
- Most index one-liners (14–39) — spot-check the load-bearing ones.
Verified already (do not re-check): APEC, Qeshm/Kuwait, Voyager, EU €45bn,
Peltola 56–44, gold $3,788, COP31 draft, UK 3.6% / euro 4.0%, El Obeid 37.

### 3. Tighten the grid typography
Some grid headlines are cramped at 1024px. Check every dek for clipping,
especially "MIDNIGHT IN NZ" (edge-clipped) and the €45bn panel. Shorten deks
rather than shrinking type below legibility — the judge rewards "it reads".

### 4. Un-crowd the map
The Europe dot cluster (London / Brussels / Kyiv / Antalya / Kuwait) is tight.
Spread the dots or use short leader lines. The Washington/NY pair overlaps
slightly — separate them.

### 5. Phone legibility pass
The user reads the render on his phone. View `entry.png` at phone size: the
index lines (14–39) and the footer sources line are the smallest text — if
they blur into grey, raise their size or cut the weakest index items. Never
cut the 13 featured stories to make room; trim the index first.

### 6. Story-count check
Top entries carry 30–43 stories. Ours has 39. If a variant with fewer, better
stories reads cleaner, try it — but keep the date, the 3 heroes, the map and
the stat strip in every variant.

### 7. A/B variants (only after 1–5)
Render 2–3 variants (e.g. different hero-1 art, different grid density),
view them side by side, keep the strongest. Do not submit variants to
make.fun yourself — the main agent submits the chosen one (only the latest
submission counts, and a resubmit replaces the current #174 entry).

## How to know it worked

There is no local judge. The signal is the dev leaderboard after the main
agent re-submits the improved image: rank and judge win rate move (or not).
Re-submission happens only through the main agent, before entries close
**2026-11-20 00:00 UTC** (19 Nov, 19:00 EST).
