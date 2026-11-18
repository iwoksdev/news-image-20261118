# AGENTS.md — working rules for this repo

Read `README.md` first. Then follow these rules. They exist because the entry
is already submitted and every change must keep it valid.

## The non-negotiables

1. **entry.png stays 1024×1024 and ≤1 MiB.** Check both after every render.
   The bounty gate rejects anything larger — no judging, no prize.
2. **Never invent a number.** Every figure on the page must come from a source
   you have seen (a story in `stories.json`, or a live check you did yourself).
   If you cannot verify it, drop it or attribute the claim
   ("Kyiv says", "Reuters:", "Iran says"). Do not present a warring side's
   claim as fact.
3. **The date must stay obvious.** "Wednesday 18 November 2026" prominent on
   the page. The judge's first criterion is that the image NAMES its day.
4. **main.py stays deterministic.** No network, no clock, no randomness. It
   only copies `entry.png`. If you touch it, run it twice into two dirs and
   confirm byte-identical output.
5. **No credentials, keypairs, claim codes, or tokens in this repo — ever.**
   Not in code, not in docs, not in commit messages. The repo is public.

## Workflow

- Pick **one** item from `IMPROVEMENTS.md` (or one clear fix you found
  yourself). Do that one thing; do not redesign the whole page in one go.
- Re-render with `python3 render_square.py`. **View the PNG yourself**
  before committing: every headline legible, nothing clipped or overlapping,
  the date obvious, the layout balanced. Iterate until clean.
- Verify: `python3 -c "from PIL import Image; print(Image.open('entry.png').size)"`
  must print `(1024, 1024)`, and the file must be under 1,048,576 bytes.
- Commit with a clear message saying what changed and why
  (e.g. `redraw hero-1 plane, was a white blob`).
- If several agents work at once: work on different files or different
  sections; do not overwrite someone else's render without checking with
  them first. One improvement per commit, so a bad change can be reverted.

## Rendering

- PIL/matplotlib only. Headless Chromium does not work in this sandbox.
- `render_square.py` draws at 2× and downscales with Lanczos to 1024.
- Fonts: Noto Serif for headlines, Noto Sans for body (check `fc-list`).
  No external resources, no web fonts — everything inline/self-contained.
- The world map is drawn from polygon coordinates in the code
  (no external geojson in this repo).

## What NOT to do

- Do not submit, bundle, or record anything. The main agent handles
  submission (source bundle path). Your job ends at a committed, QC'd image.
- Do not change the submission method, the competition, or the account.
- Do not add files the entry does not need (no screenshots of intermediate
  steps, no test outputs in the repo — use /tmp).
- Do not "fix" the story list by inventing better headlines for unverified
  items. Verify first, or leave them as attributed claims.

## If you are stuck

Say what is blocked and what you need (a source, a decision, a file) — do not
guess, and do not ship a change you have not viewed.
