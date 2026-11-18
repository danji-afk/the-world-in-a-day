# The World in a Day

A 1024 × 1024 RGB newspaper front page for Tuesday, 17 November 2026, with an oversized date, three illustrated lead stories, eight dispatch cards, and compact world briefs. Earlier or upcoming events carry explicit dates.

Render the artwork with `python3 render.py` (requires Pillow and system DejaVu fonts).

Export the finished PNG with Node 22: `MAKEFUN_OUTPUT_DIR=/output node main.ts`. The entry point copies the bundled `entry.png` from its own directory; the output directory defaults to `/output`.

Rendering and export use no network, randomness, or timestamps. The TypeScript entry point uses only Node's standard library.
