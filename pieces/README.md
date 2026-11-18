# pieces/ — standalone page pieces (2x their slot)

Each piece is a PNG at 2x its slot on the 1024x1024 page plus the script that
drew it. The main agent composites pieces onto the final image; nothing here
touches `entry.png` or `main.py`.

| Piece | File | Slot (1x) | Output |
|---|---|---|---|
| 3 · Hero 1 — APEC Shenzhen, Xi greets Trump | `hero1.py` → `hero1.png` | 323 x 228 at x 16, y 145 (art 323 x 102 on top) | 646 x 456, solid paper (247,242,227) |

Run: `python3 pieces/hero1.py` (needs Pillow; reads `../stories.json`, `../fonts`).
