# The Day in World News — Wednesday 18 November 2026

Entry for the make.fun bounty **news-image-20261118** ("Sum up 18 November's
world news in one image").

`main.py` renders a 1024×1024 newspaper-style front page at runtime with
Pillow — nothing is pre-rendered. It writes exactly one PNG,
`news-image-20261118.png`, to the directory named by `$MAKEFUN_OUTPUT_DIR`
(fallback `/output`).

```
pip install pillow
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

- Python standard library + Pillow only; no network; runs in about a second.
- Deterministic: no clocks, no `random`; star fields use a fixed LCG; the
  PNG is saved with fixed options, so two runs are byte-identical.
- Drawn at 2× and downsampled with LANCZOS for soft anti-aliased edges.
- Fonts (`./fonts`, SIL OFL): Playfair Display for masthead and headlines,
  PT Serif / PT Serif Italic for deks, body and the subtitle, Inter Bold in
  tracked uppercase for labels, kickers and the date line.
- All text, the world map outlines and the illustrations (Trump and Xi beside
  their flags, the Gulf inset, Voyager 1) are coded in `main.py`.

Facts are limited to what was verified in 18 November reporting; contested
claims are attributed inline ("Kyiv says", "Iran says", "TASS reports").

Licence: MIT (see `LICENSE`); fonts under their own OFL licence.
