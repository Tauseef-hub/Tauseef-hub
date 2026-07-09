#!/usr/bin/env python3
"""
make_banner.py — generates the profile README banner (dark + light SVG)
from REAL retail turnover data produced by the Australian Retail
Intelligence pipeline.

Input : assets/retail_series.csv  (columns: date,value — real data only)
Output: assets/banner_dark.svg, assets/banner_light.svg

No third-party dependencies. If the CSV is missing, this script STOPS —
it never fabricates data.
"""

import csv
import os
import sys

W, H = 1280, 300
PAD = 24

CSV_PATH = os.path.join("assets", "retail_series.csv")

THEMES = {
    "dark": {
        "bg": "#161b22", "border": "#30363d",
        "spark": "#2dd4bf", "area_opacity": "0.14",
        "text": "#e6edf3", "sub": "#8b949e", "cap": "#6e7681",
        "file": os.path.join("assets", "banner_dark.svg"),
    },
    "light": {
        "bg": "#f6f8fa", "border": "#d0d7de",
        "spark": "#1f3864", "area_opacity": "0.10",
        "text": "#1f2328", "sub": "#57606a", "cap": "#6e7781",
        "file": os.path.join("assets", "banner_light.svg"),
    },
}

NAME = "TAUSEEF MOHAMMED AOUN"
TAGLINE = "Data Science \u00b7 Monash University \u00b7 Systems that ship"
CAPTION = "background: real ABS retail turnover (1982\u20132024), processed by my pipeline"
FONT = "'Segoe UI', Helvetica, Arial, sans-serif"


def load_series(path):
    if not os.path.exists(path):
        sys.exit(
            f"ERROR: {path} not found.\n"
            "Export a REAL national monthly turnover series from the retail "
            "project (pipeline output or live API) with columns date,value.\n"
            "This script does not fabricate data."
        )
    vals = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            try:
                vals.append(float(row["value"]))
            except (KeyError, ValueError):
                continue
    if len(vals) < 24:
        sys.exit(f"ERROR: only {len(vals)} usable rows in {path}; need >= 24.")
    # Downsample to ~180 points so the polyline stays crisp
    if len(vals) > 180:
        step = len(vals) / 180.0
        vals = [vals[int(i * step)] for i in range(180)]
    return vals


def spark_points(vals):
    lo, hi = min(vals), max(vals)
    rng = (hi - lo) or 1.0
    x0, x1 = PAD, W - PAD
    # Chart occupies the lower band of the banner, under the text
    y_top, y_bot = 150, H - PAD
    pts = []
    n = len(vals)
    for i, v in enumerate(vals):
        x = x0 + (x1 - x0) * (i / (n - 1))
        y = y_bot - (y_bot - y_top) * ((v - lo) / rng)
        pts.append((round(x, 1), round(y, 1)))
    return pts, y_bot


def svg(theme, vals):
    t = THEMES[theme]
    pts, y_bot = spark_points(vals)
    line = " ".join(f"{x},{y}" for x, y in pts)
    area = f"{PAD},{y_bot} " + line + f" {W - PAD},{y_bot}"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"
     viewBox="0 0 {W} {H}" role="img"
     aria-label="Tauseef Mohammed Aoun - Data Science, Monash University">
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16"
        fill="{t['bg']}" stroke="{t['border']}" stroke-width="1.5"/>
  <polygon points="{area}" fill="{t['spark']}" opacity="{t['area_opacity']}"/>
  <polyline points="{line}" fill="none" stroke="{t['spark']}"
            stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>
  <text x="{PAD + 16}" y="86" font-family="{FONT}" font-size="46"
        font-weight="700" letter-spacing="1.5" fill="{t['text']}">{NAME}</text>
  <text x="{PAD + 18}" y="124" font-family="{FONT}" font-size="21"
        fill="{t['sub']}">{TAGLINE}</text>
  <text x="{W - PAD - 12}" y="{H - 14}" font-family="{FONT}" font-size="11.5"
        fill="{t['cap']}" text-anchor="end">{CAPTION}</text>
</svg>
"""


def main():
    vals = load_series(CSV_PATH)
    os.makedirs("assets", exist_ok=True)
    for theme in THEMES:
        out = THEMES[theme]["file"]
        with open(out, "w") as f:
            f.write(svg(theme, vals))
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
