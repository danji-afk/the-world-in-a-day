[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/danji-afk/the-world-in-a-day/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/danji-afk/the-world-in-a-day/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

# The World in a Day

A 1024 × 1024 RGB newspaper front page for Tuesday, 17 November 2026, with an oversized date, three illustrated lead stories, eight dispatches, twelve additional world cards, and eighteen compact world briefs (41 stories total). Earlier or upcoming events carry explicit dates.

Render the artwork with `python3 render.py` (requires Pillow and system DejaVu fonts).

Export the finished PNG with Node 22: `MAKEFUN_OUTPUT_DIR=/output node main.ts`. The entry point copies the bundled `entry.png` from its own directory; the output directory defaults to `/output`.

Rendering and export use no network, randomness, or timestamps. The TypeScript entry point uses only Node's standard library.
