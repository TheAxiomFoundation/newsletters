#!/usr/bin/env python3
"""Render the PolicyBench top-10 card used in the newsletter.

The snapshot date must be the one PolicyBench itself publishes (the
"SNAPSHOT YYYY-MM-DD" line on policybench.org), not the day we drew the
chart. Bars are proportional to the leader's score.
"""
import json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TRACK = 638  # px, width of the leader's bar

def render(spec, out_png):
    rows = spec["rows"]
    top = max(r["score"] for r in rows)
    html = (HERE / "card.html").read_text(encoding="utf-8")
    trs = []
    for i, r in enumerate(rows, 1):
        w = round(r["score"] / top * TRACK)
        trs.append(
            f'<tr><td class="rank">{i}</td>'
            f'<td class="name">{r["name"]}</td>'
            f'<td class="track"><div class="bar" style="width:{w}px"></div></td>'
            f'<td class="score">{r["score"]:.1f}%</td></tr>'
        )
    html = (html.replace("__TITLE__", spec["title"])
                .replace("__SUB1__", spec["sub1"])
                .replace("__SUB2__", spec["sub2"])
                .replace("__FOOT__", spec["foot"])
                .replace("__ROWS__", "".join(trs)))
    tmp = HERE / "_render.html"
    tmp.write_text(html, encoding="utf-8")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--window-size=1200,840",
                    f"--screenshot={out_png}", "--default-background-color=FAF9F5FF",
                    "--virtual-time-budget=9000", tmp.as_uri()],
                   check=True, capture_output=True)
    tmp.unlink()

if __name__ == "__main__":
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    render(spec, sys.argv[2])
    print("wrote", sys.argv[2])
