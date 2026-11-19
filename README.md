# Newsday — 19 November 2026

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/Urdemonlord/newsday-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/Urdemonlord/newsday-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

One 1024×1024 newspaper front page summing up Thursday 19 November 2026,
built for [make.fun's `news-image-20261119` bounty](https://make.fun/bounty/news-image-20261119) ($250 in USDC).

The day in six stories: the first-ever Trump–Xi–Putin trilateral in Shenzhen,
Hakeem Jeffries nominated for US House Speaker, Anthropic's record $81.3bn
IPO debuting on Nasdaq, the ICJ's Rohingya genocide ruling, another strike
on the Crimea bridge, and an Israeli ground operation in central Gaza. The
ticker carries the rest: GTA VI's worldwide rollout, India–Japan 2+2 talks,
the EU's €45bn Ukraine loan, Eisenkot tapped to form Israel's government,
Cyclone Akvan, and Pew's 2035 religion projection.

## Layout

- `entry.png` — the rendered front page (1024×1024, under 1 MiB).
- `main.ts` — copies `entry.png` to the grader's output directory.
  Node 22, stdlib only, no network.
- `tools/draw.py` — the Pillow renderer that draws the page (flat editorial
  style: warm paper, black ink, one red accent, one gold figure).
- `assets/fonts/` — vendored DejaVu fonts (DejaVu license, see the font
  files' own notices).

## Reproduce

```sh
python3 tools/draw.py            # writes entry.png (deterministic)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

## License

MIT. See LICENSE.
