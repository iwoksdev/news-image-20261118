# Notes for agents working on this repo

- The entry is `main.py`. It must render the image itself with Pillow at
  runtime (no pre-made PNG), write one 1024×1024 PNG ≤ 1 MiB to
  `$MAKEFUN_OUTPUT_DIR` (fallback `/output`), stay deterministic (no
  clocks, no `random`), use only the standard library + Pillow, and finish
  in under 60 s.
- Fonts come from `./fonts` only: Playfair Display (masthead, headlines),
  PT Serif / Italic (deks, body, subtitle), Inter Bold tracked caps
  (labels, kickers, date line). Three families, no system or web fonts.
- Page text lives in the `HEROES`, `NUMBERS` and `INDEX` tables near the
  top of `main.py`. `Page.para()` prints a `WARNING` on overflow; the index
  flow prints a warning if it runs out of columns. Keep renders warning-free.
- Only verified facts; attribute disputed claims; never invent numbers.
- Never submit to make.fun from here; the owner handles submission.
