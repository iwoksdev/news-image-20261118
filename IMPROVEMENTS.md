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

## Done (18 Nov, redesign branch)

- Renderer rewritten: real Natural Earth coastlines (world map + Gulf /
  Bay of Bengal / Horn insets), proper airliner + flags + red carpet for
  hero 1, Voyager dish/boom + dimension bracket, Playfair Display masthead,
  larger grid/index type, art panels clipped on sub-canvases, dots for all
  39 stories on the map, overflow warnings instead of silent truncation.
- Verified the previously unflagged items (141/126 drones, Akvan, Ethiopia–
  Eritrea, GTA VI 11:00 UTC) against 18 Nov reporting; Akvan upgraded to
  "Severe Cyclonic Storm", Odesa toll "four"; weak Peru no-damage quake
  swapped for UK sanctions on eight settlement-linked firms (London).

- Refinement pass (in place, layout untouched): 4x supersample; owner's
  fonts (Playfair heads, EB Garamond deks/index, DM Serif Display Italic
  stat numbers); detailed hero-1 tarmac scene (VC-25-style aircraft, air
  stair, Xi/Trump, CN-US flag line, Ping An spire); Gulf graticule + Hormuz
  + cities; Voyager Milky Way band, terminator, glint; Alaska outline in the
  Senate card; Bay of Bengal graticule + Visakhapatnam/Chennai; Horn cities
  + Red Sea; world-map graticule + sea gradient; soft panel shadows.

- Hero-zone pass: two-column hero (lead APEC story at 60% width with a
  two-figure Trump/Xi illustration beside correct US and Chinese flags on a
  shared ground line; Iran-war and Voyager heroes stacked at 40%, one
  12 px gutter, edges aligned); NYT three-font system (Playfair Display
  headlines, PT Serif deks/index, Inter Bold tracked caps for labels);
  headlines rewritten as specific hooks and deks as complete sentences.

## Ranked ideas (remaining)

### 1. Hero art polish
Hero 1 is now a recognisable airliner on a tarmac; further gains are in the
small figures (Xi/Trump) and the air stair. Keep it flat and clean — the
judge sees it at 1024px.

### 2. Spot-check the index one-liners (14–39)
Heroes, grid and the four formerly-flagged items are verified. The index
lines were carried over from the reference; spot-check the load-bearing
ones with a live source and shorten/attribute anything shaky.

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
