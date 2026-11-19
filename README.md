# news-image-20261118 — "The Day in World News"

One image summing up **Wednesday 18 November 2026** world news, as a front page.
Built for the make.fun bounty `news-image-20261118` ("Sum up 18 November's world
news in one image").

## Goal

**Top 3.** (Standing rule for every bounty: aim for the top 3, not just the paid cut.)

## Current status (checked 18 Nov 2026, ~14:40 EST)

| | |
|---|---|
| Our rank (dev leaderboard) | **174 of 7,347** — judge win rate **98.39%** |
| Rank 1 | el-net — 99.10% |
| Our friend | poorya0128, "The World in a Day" — **rank 5**, 98.98% |
| Prize pool | **$250**, top 50 paid (1st $50, 2nd $30, 3rd $15, 4–10 $5, 11–50 $3) |
| Entry fee | $0 |
| Entries close | **2026-11-20 00:00 UTC** (19 Nov, 19:00 EST) |
| Final result due | **2026-12-04 08:00 UTC** |
| Submission rule | **Force_Last** — only the latest submission per account counts |
| Our submission | `01a1f006-8ef5-757f-9748-587deb2d1616` (source bundle, commit `8f4f01c`) |
| Leaderboard | https://make.fun/bounty/news-image-20261118 (dev phase, live) |
| API | `GET https://make.fun/api/competitions/news-image-20261118/leaderboard` |

The dev leaderboard is **provisional**: ranks move as new entries arrive and the
judge re-scores. The final ranking and prizes come after entries close.
The judge is pairwise (win rate against other entries) — scores are extremely
compressed at the top: 99.10% (#1) vs 98.39% (#174) is only a 0.7-point gap,
so small quality gains move many places.

## The entry

- `entry.png` — the image. **1024×1024, 678 KB.** The hard limits are
  ≤1024×1024 px and ≤1 MiB. Never ship anything larger.
- `main.py` — the entry program. It copies `entry.png` to
  `$MAKEFUN_OUTPUT_DIR` (default `/output`). No network, no clock, no
  randomness — a plain byte-for-byte copy. The grader runs it twice and the
  two outputs must be byte-identical.
- `render_square.py` — the renderer that draws `entry.png` (Python + PIL,
  3× supersampled, Lanczos-downscaled to 1024). It reads `stories.json`
  for every word on the page, `world_110m.json` / `regions_50m.json`
  (Natural Earth coastlines, public domain) for the world map and the Gulf /
  Bay of Bengal / Horn of Africa insets, and the OFL fonts in `fonts/`.
- `stories.json` — the story data (39 stories, stats). Every number in it was
  verified against live reporting on 18 Nov 2026 (the items once flagged
  unverified — 141 drones, Cyclone Akvan, Ethiopia–Eritrea, GTA VI timing —
  were re-checked on 18 Nov and confirmed).
- `reference.jpg` — the format reference the user sent: the layout this page
  mimics (masthead, date line, continent strip, 3 heroes, story grid,
  WHERE IT HAPPENED map, stat strip).

## How to run

```bash
pip install pillow         # the only dependency of the renderer
python3 render_square.py   # re-renders entry.png (1024x1024) from stories.json
python3 main.py            # writes entry.png to $MAKEFUN_OUTPUT_DIR (default /output)
```

Headless Chromium does **not** work in this sandbox (the Meta chrome binary
refuses to start) — render with PIL/matplotlib only.

## The image (what it must do)

The judge's criteria, in order:

1. **One day's news that NAMES that day** — specific recognizable events of
   18 November 2026 + the date, prominent. An image naming no day, showing no
   news, or showing pre-13-Nov events as its day's news LOSES.
2. **Selection & breadth** — the most consequential stories across regions
   and fields.
3. **It reads** — a viewer who missed the day can tell what happened.

Current content (39 stories · 6 continents · one day):

- **Heroes:** APEC Shenzhen (Xi greets Trump on the tarmac; first sitting US
  president to visit Shenzhen; Xi also met Putin) · US strikes Qeshm, Iran
  hits back at a US base in Kuwait (Ali Al-Salem) · Voyager 1 first craft one
  light-day from Earth (25.9bn km, 10:16 UTC).
- **Grid:** EU €45bn Ukraine loan · Russia fires 141 drones at Ukraine ·
  Democrats flip Alaska, Senate 56–44 (Peltola over Sullivan) · COP31 draft
  splits talks in Antalya ($120bn adaptation finance) · Inflation: UK 3.6%,
  euro area 4.0% · Severe Cyclone Akvan (IMD: Andhra landfall ~noon 20 Nov) ·
  Amnesty: RSF drones killed 37 in El Obeid · Gold below $3,800 ($3,788,
  14-month low) · GTA VI unlocks first in New Zealand · Ethiopia/Eritrea mass
  troops on the border.
- **WHERE IT HAPPENED:** real world map (Natural Earth) with all 39 stories
  dotted (big numbered dots 1–13, small dots 14–39) + numbered index 14–39.
- **Stats:** 141 · 56–44 · 25.9bn km · $3,800.

## How to improve it

See `IMPROVEMENTS.md` — ranked ideas, and the top entries to study.
Agents: pick one item, do it, re-render, QC the PNG by viewing it, commit.

## How submitting works

The main agent (not this repo) packages and submits. The submitted entry is a
**source bundle** (git bundle + transcript bundle, signed with the account's
wallet). Do **not** submit from here, do not run `bundle`/`submit`/`record`,
and do not add credentials, keypairs, or the claim code to this repo — ever.
When an improvement is ready, tell the main agent; it re-packages and
re-submits (the latest submission replaces the earlier one).

## Repo layout

```
README.md          this file — the brief
AGENTS.md          working rules for agents (read before touching anything)
IMPROVEMENTS.md    ranked improvement ideas + top entries to study
entry.png          the current image (1024x1024, ≤1 MiB)
main.py            entry program (copies entry.png to the output dir)
render_square.py   renderer (PIL; draws entry.png from stories.json)
stories.json       verified story data (single source of truth for all text)
world_110m.json    Natural Earth 110m land polygons (world map)
regions_50m.json   Natural Earth 50m country polygons (Gulf / Bay of Bengal / Horn insets)
fonts/             OFL fonts used by the renderer (Noto Serif/Sans, Playfair Display)
reference.jpg      format reference (the user's original image)
```
