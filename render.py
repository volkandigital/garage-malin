"""Le Garage Malin — générateur de carrousels Instagram (1080x1350).
Usage : python3 render.py posts/<post>.json  -> out/<post>/slide-N.png
"""
import json, sys, html, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).parent
FONTS = (ROOT / "fonts").resolve().as_uri()
HANDLE = "@legaragemalin"

CSS = f"""
@font-face{{font-family:Anton;src:url({FONTS}/anton-latin-400-normal.woff2)}}
@font-face{{font-family:Inter;font-weight:400;src:url({FONTS}/inter-latin-400-normal.woff2)}}
@font-face{{font-family:Inter;font-weight:600;src:url({FONTS}/inter-latin-600-normal.woff2)}}
@font-face{{font-family:Inter;font-weight:800;src:url({FONTS}/inter-latin-800-normal.woff2)}}
:root{{--bg:#121417;--card:#1C1F24;--line:#2A2E35;--y:#FFC21A;--w:#F5F5F2;--g:#9BA1A9;--ok:#3DDC84;--ko:#FF5A4E}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;background:var(--bg);color:var(--w);font-family:Inter;position:relative;overflow:hidden}}
body:before{{content:"";position:absolute;inset:0;background:
 radial-gradient(900px 600px at 85% -10%,rgba(255,194,26,.10),transparent 60%),
 repeating-linear-gradient(0deg,rgba(255,255,255,.018) 0 2px,transparent 2px 6px)}}
.top{{position:absolute;top:64px;left:80px;right:80px;display:flex;justify-content:space-between;align-items:center}}
.logo{{display:flex;align-items:center;gap:18px;font-family:Anton;font-size:34px;letter-spacing:1px}}
.badge{{width:62px;height:62px;border-radius:16px;background:var(--y);color:var(--bg);display:grid;place-items:center;font-size:30px}}
.logo b{{color:var(--y);font-weight:400}}
.count{{font-weight:600;color:var(--g);font-size:28px}}
.road{{position:absolute;left:0;right:0;bottom:70px;height:10px;background:repeating-linear-gradient(90deg,var(--y) 0 70px,transparent 70px 120px);opacity:.9}}
.main{{position:absolute;top:200px;left:80px;right:80px;bottom:150px;display:flex;flex-direction:column}}
.tag{{align-self:flex-start;background:var(--y);color:var(--bg);font-weight:800;font-size:28px;letter-spacing:2px;padding:12px 24px;border-radius:10px}}
h1{{font-family:Anton;font-weight:400;font-size:150px;line-height:.95;text-transform:uppercase;margin-top:40px}}
h2{{font-family:Anton;font-weight:400;font-size:96px;line-height:1;text-transform:uppercase;margin-bottom:50px}}
h2 span,h1 span{{color:var(--y)}}
.sub{{font-size:46px;font-weight:600;line-height:1.25;color:var(--w);margin-top:36px;max-width:880px}}
.car{{margin-top:auto;width:88%;align-self:center}}
.swipe{{align-self:flex-end;margin-top:24px;font-weight:800;font-size:34px;color:var(--y)}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:28px;flex:1}}
.stat{{display:flex;flex-direction:column;justify-content:center;background:var(--card);border:2px solid var(--line);border-radius:28px;padding:36px}}
.stat .l{{font-size:26px;font-weight:600;color:var(--g);text-transform:uppercase;letter-spacing:1.5px}}
.stat .v{{font-family:Anton;font-size:64px;line-height:1.05;margin-top:14px;color:var(--y)}}
.stat .n{{font-size:28px;margin-top:12px;line-height:1.3}}
.items{{display:flex;flex-direction:column;gap:26px}}
.it{{display:flex;gap:28px;align-items:flex-start;background:var(--card);border:2px solid var(--line);border-radius:24px;padding:30px 34px}}
.ic{{flex:none;width:56px;height:56px;border-radius:50%;display:grid;place-items:center;font-weight:800;font-size:32px;color:var(--bg)}}
.pro .ic{{background:var(--ok)}} .con .ic{{background:var(--ko)}}
.it .t{{font-size:38px;font-weight:800;line-height:1.2}}
.it .d{{font-size:29px;color:var(--g);margin-top:8px;line-height:1.3}}
.score{{font-family:Anton;font-size:300px;line-height:1;color:var(--y)}}
.score small{{font-size:120px;color:var(--g)}}
.verdict{{font-size:46px;font-weight:600;line-height:1.3;margin-top:30px}}
.for{{margin-top:44px;background:var(--card);border-left:10px solid var(--y);border-radius:16px;padding:30px 36px;font-size:34px;line-height:1.35}}
.cta h1{{font-size:130px}}
.acts{{display:flex;flex-direction:column;gap:30px;margin-top:60px}}
.act{{font-size:44px;font-weight:800;display:flex;gap:26px;align-items:center}}
.act i{{font-style:normal;width:80px;height:80px;border-radius:22px;background:var(--card);border:2px solid var(--line);display:grid;place-items:center;font-size:42px}}
.q{{margin-top:auto;background:var(--y);color:var(--bg);border-radius:28px;padding:40px;font-size:42px;font-weight:800;line-height:1.25}}
.src{{position:absolute;left:80px;right:80px;bottom:100px;font-size:20px;color:#6B7178}}
"""

CAR = """<svg class="car" viewBox="0 0 920 330" xmlns="http://www.w3.org/2000/svg">
<ellipse cx="460" cy="300" rx="420" ry="18" fill="#000" opacity=".45"/>
<path d="M60 230 C60 190 80 175 120 168 L250 150 C300 95 360 62 450 58 L600 58 C660 60 700 80 745 140 L820 152 C860 160 875 185 872 230 L872 248 L60 248 Z" fill="#1F2329" stroke="#FFC21A" stroke-width="6" stroke-linejoin="round"/>
<path d="M285 150 C330 104 375 82 450 80 L520 80 L520 150 Z M545 80 L600 80 C645 82 680 100 715 150 L545 150 Z" fill="#2C323A"/>
<line x1="120" y1="190" x2="860" y2="190" stroke="#FFC21A" stroke-width="3" opacity=".5"/>
<circle cx="230" cy="248" r="58" fill="#121417" stroke="#F5F5F2" stroke-width="8"/><circle cx="230" cy="248" r="22" fill="#FFC21A"/>
<circle cx="700" cy="248" r="58" fill="#121417" stroke="#F5F5F2" stroke-width="8"/><circle cx="700" cy="248" r="22" fill="#FFC21A"/>
<rect x="840" y="175" width="30" height="16" rx="5" fill="#FFC21A"/>
</svg>"""

e = lambda s: html.escape(str(s))


def frame(body, i, n, source=None):
    src = f'<div class="src">Sources : {e(source)}</div>' if source else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="top"><div class="logo"><div class="badge">GM</div>LE GARAGE <b>MALIN</b></div><div class="count">{i}/{n}</div></div>
<div class="main">{body}</div>{src}<div class="road"></div></body></html>"""


def slide(s):
    t = s["type"]
    if t == "cover":
        return (f'<div class="tag">{e(s["tag"])}</div><h1>{s["title"]}</h1>'
                f'<div class="sub">{e(s["subtitle"])}</div>{CAR}<div class="swipe">GLISSE →</div>')
    if t == "stats":
        cards = "".join(f'<div class="stat"><div class="l">{e(c["label"])}</div><div class="v">{e(c["value"])}</div>'
                        f'<div class="n">{e(c.get("note",""))}</div></div>' for c in s["cards"])
        return f'<h2>{s["title"]}</h2><div class="grid">{cards}</div>'
    if t in ("pros", "cons"):
        ic = "✓" if t == "pros" else "!"
        its = "".join(f'<div class="it {t[:-1]}"><div class="ic">{ic}</div><div><div class="t">{e(x["t"])}</div>'
                      f'<div class="d">{e(x.get("d",""))}</div></div></div>' for x in s["items"])
        return f'<h2>{s["title"]}</h2><div class="items">{its}</div>'
    if t == "verdict":
        return (f'<h2>{s["title"]}</h2><div class="score">{e(s["score"])}{"<small>/10</small>" if str(s["score"]).isdigit() else ""}</div>'
                f'<div class="verdict">{e(s["text"])}</div><div class="for"><b>Pour qui ?</b> {e(s["for"])}</div>')
    if t == "cta":
        return (f'<div class="cta"><h1>T\'AS <span>AIMÉ ?</span></h1></div><div class="acts">'
                f'<div class="act"><i>🔖</i>Enregistre pour ton prochain achat</div>'
                f'<div class="act"><i>📤</i>Envoie à un pote qui cherche une voiture</div>'
                f'<div class="act"><i>➕</i>Abonne-toi : {HANDLE}</div></div><div class="q">{e(s["question"])}</div>')
    raise ValueError(t)


def render(path):
    post = json.loads(pathlib.Path(path).read_text())
    out = ROOT / "out" / pathlib.Path(path).stem
    out.mkdir(parents=True, exist_ok=True)
    n = len(post["slides"])
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, s in enumerate(post["slides"], 1):
            src = post.get("sources") if i == n - 1 else None
            pg.set_content(frame(slide(s), i, n, src), wait_until="load")
            pg.evaluate("document.fonts.ready")
            pg.screenshot(path=str(out / f"slide-{i}.jpg"), type="jpeg", quality=92)
        b.close()
    (out / "legende.txt").write_text(post["caption"] + "\n\n" + " ".join(post["hashtags"]))
    print(out)


if __name__ == "__main__":
    render(sys.argv[1])
