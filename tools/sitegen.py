#!/usr/bin/env python3
"""The Morning Commit site generator (no build step on GitHub; run locally before pushing).

  python3 tools/sitegen.py add DATE SRC_DIR [--title T] [--lead L] [--thumb img/x.jpg]
      Copy SRC_DIR/index.html (+ SRC_DIR/img/*) into editions/DATE/, compress images to
      WebP (max 1200px wide, q80) and rewrite their references, add/replace the entry in
      editions.json, then run `rebuild`.
  python3 tools/sitegen.py rebuild
      Re-inject the shared head/nav/footer into every edition, regenerate index.html
      (= latest edition, via <base>), archive/index.html, and bump the service-worker cache.
"""
import argparse, datetime as dt, html, json, os, re, shutil, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "editions.json"
E = html.escape
SITE = "https://kayraucklnc.github.io/morning-commit/"
IMG_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

def load():
    return json.loads(MANIFEST.read_text()) if MANIFEST.exists() else []

def save(items):
    items.sort(key=lambda x: x["date"], reverse=True)
    MANIFEST.write_text(json.dumps(items, indent=2, ensure_ascii=False) + "\n")

def nice(date, short=False):
    d = dt.date.fromisoformat(date)
    return d.strftime("%a %-d %b") if short else d.strftime("%A, %B %-d, %Y")

def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()

def compress(src, dst_dir, max_w=1200, q=80):
    from PIL import Image
    im = Image.open(src)
    if getattr(im, "is_animated", False):
        out = dst_dir / src.name; shutil.copy2(src, out); return out.name
    im = im.convert("RGBA") if im.mode in ("P", "LA", "RGBA") else im.convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    out = dst_dir / (src.stem + ".webp")
    im.save(out, "WEBP", quality=q, method=6)
    return out.name

def add(date, src, title=None, lead=None, thumb=None):
    dt.date.fromisoformat(date)  # validate
    src = Path(src)
    page = (src / "index.html").read_text()
    dst = ROOT / "editions" / date
    if dst.exists(): shutil.rmtree(dst)
    (dst / "img").mkdir(parents=True)
    if (src / "img").is_dir():
        for f in sorted((src / "img").iterdir()):
            if f.suffix.lower() not in IMG_EXT: continue
            if f"img/{f.name}" not in page:  # skip images the page never uses
                continue
            new = compress(f, dst / "img")
            page = page.replace(f"img/{f.name}", f"img/{new}")
            if thumb == f"img/{f.name}": thumb = f"img/{new}"
    # metadata: explicit args > <meta name="mc:*"> > first <h2>/.deck/<img>
    def meta(n):
        m = re.search(rf'<meta name="mc:{n}" content="([^"]*)"', page); return html.unescape(m.group(1)) if m else None
    lead = lead or meta("lead") or strip_tags((re.search(r"<h2[^>]*>(.*?)</h2>", page, re.S) or [None, ""])[1])
    deck = meta("deck") or strip_tags((re.search(r'class="deck"[^>]*>(.*?)</p>', page, re.S) or [None, ""])[1])
    title = title or meta("title") or f"The Morning Commit · {nice(date)}"
    thumb = thumb or meta("thumb") or (re.search(r'<img[^>]+src="(img/[^"]+)"', page) or [None, None])[1]
    if thumb:
        from PIL import Image
        im = Image.open(dst / thumb).convert("RGB"); im.thumbnail((640, 640))
        im.save(dst / "img" / "_thumb.webp", "WEBP", quality=78); thumb = "img/_thumb.webp"
    (dst / "index.html").write_text(page)
    items = [i for i in load() if i["date"] != date]
    items.append(dict(date=date, title=title, lead=lead, deck=deck,
                      thumb=f"editions/{date}/{thumb}" if thumb else None, path=f"editions/{date}/"))
    save(items)
    rebuild()

HEAD = """<!--mc:head-->
<meta name="theme-color" content="#141414">
<meta name="color-scheme" content="light">
<link rel="manifest" href="{r}manifest.webmanifest">
<link rel="icon" type="image/png" sizes="48x48" href="{r}assets/icons/favicon-48.png">
<link rel="icon" type="image/png" sizes="192x192" href="{r}assets/icons/icon-192.png">
<link rel="apple-touch-icon" href="{r}assets/icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Morning Commit">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{lead}">
{ogimg}<script>if(matchMedia("(max-width:760px)").matches)document.documentElement.classList.add("mc-phone");</script>
<script defer src="{r}assets/app.js?v={v}"></script>
<!--/mc:head-->"""

def navbar(items, i, r):
    newer = items[i - 1] if i > 0 else None
    older = items[i + 1] if i + 1 < len(items) else None
    o = f'<a href="{r}{older["path"]}" rel="prev" aria-label="Older edition">‹ <i class="lbl">{nice(older["date"], True)}</i></a>' if older else '<span>‹</span>'
    n = f'<a href="{r}{newer["path"]}" rel="next" aria-label="Newer edition"><i class="lbl">{nice(newer["date"], True)}</i> ›</a>' if newer else '<span>›</span>'
    top = f'<!--mc:nav--><nav class="mcnav"><div class="in"><a class="home" href="{r}">The Morning Commit</a><div class="pn">{o}<a href="{r}archive/">Archive</a>{n}</div></div></nav><!--/mc:nav-->'
    bot = f'<!--mc:foot--><div class="mcfoot">{o.replace("rel=", "data-r=")}<a href="{r}archive/">All editions</a>{n.replace("rel=", "data-r=")}</div><!--/mc:foot-->'
    return top, bot

def inject(page, head, top, bot, v="0"):
    page = re.sub(r"<!--mc:head-->.*?<!--/mc:head-->\n?", "", page, flags=re.S)
    page = re.sub(r"<!--mc:nav-->.*?<!--/mc:nav-->", "", page, flags=re.S)
    page = re.sub(r"<!--mc:foot-->.*?<!--/mc:foot-->", "", page, flags=re.S)
    page = re.sub(r'<base href="[^"]*">', "", page)
    page = page.replace("</head>", head + "\n</head>", 1)
    page = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + top, page, count=1)
    page = page.replace("</body>", bot + "</body>", 1)
    return bust(page, v)

def bust(page, v):
    page = re.sub(r'(assets/style\.css)(\?[^"\']*)?', rf'\1?v={v}', page)
    page = re.sub(r'(assets/app\.js)(\?[^"\']*)?', rf'\1?v={v}', page)
    if 'name="mc:built"' in page:
        page = re.sub(r'<meta name="mc:built" content="[^"]*">', f'<meta name="mc:built" content="{v}">', page)
    else:
        page = page.replace("</head>", f'<meta name="mc:built" content="{v}">\n</head>', 1)
    return page

def rebuild():
    items = load(); save(items); items = load()
    ts = str(int(time.time()))
    for i, it in enumerate(items):
        f = ROOT / it["path"] / "index.html"
        r = "../../"
        og = f'<meta property="og:image" content="{E(SITE + it["thumb"])}">\n' if it.get("thumb") else ""
        head = HEAD.format(r=r, title=E(it["title"]), lead=E(it.get("lead") or ""), ogimg=og, v=ts)
        top, bot = navbar(items, i, r)
        f.write_text(inject(f.read_text(), head, top, bot, ts))
    # home page = latest edition rendered in place; <base> makes its relative paths resolve
    if items:
        latest = items[0]
        page = (ROOT / latest["path"] / "index.html").read_text()
        page = re.sub(r"(<head[^>]*>)", lambda m: m.group(1) + f'<base href="{latest["path"]}">', page, count=1)
        (ROOT / "index.html").write_text(page)
    write_archive(items)
    sw = ROOT / "sw.js"
    if sw.exists():
        sw.write_text(re.sub(r"const VERSION = '[^']*'", f"const VERSION = 'mc-{int(time.time())}'", sw.read_text()))
    print(f"rebuilt {len(items)} edition(s); latest = {items[0]['date'] if items else None}")

def write_archive(items):
    lis = []
    for k, it in enumerate(items):
        img = f'<img src="../{E(it["thumb"])}" alt="" loading="lazy">' if it.get("thumb") else ""
        new = '<span class="new">LATEST</span>' if k == 0 else ""
        lis.append(f'<li><a href="../{E(it["path"])}">{img}<div><span class="d">{E(nice(it["date"]))}{new}</span>'
                   f'<b>{E(it.get("lead") or it["title"])}</b><p>{E(it.get("deck") or "")}</p></div></a></li>')
    body = "\n".join(lis) or '<p class="empty">No editions yet.</p>'
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Archive · The Morning Commit</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=Inter:wght@500;700;800&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/style.css">
{HEAD.format(r="../", title="Archive · The Morning Commit", lead="Every past edition of The Morning Commit", ogimg="", v=str(int(time.time())))}
</head><body><nav class="mcnav"><div class="in"><a class="home" href="../">The Morning Commit</a><div class="pn"><a href="../">Latest</a></div></div></nav>
<div class="paper arch"><header class="mast"><h1>The Archive</h1><div class="tag">Every edition of The Morning Commit, newest first · {len(items)} so far</div></header>
<ul class="alist">
{body}
</ul></div></body></html>'''
    (ROOT / "archive").mkdir(exist_ok=True)
    (ROOT / "archive" / "index.html").write_text(bust(page, str(int(time.time()))))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("add"); a.add_argument("date"); a.add_argument("src")
    a.add_argument("--title"); a.add_argument("--lead"); a.add_argument("--thumb")
    sp.add_parser("rebuild")
    x = ap.parse_args()
    add(x.date, x.src, x.title, x.lead, x.thumb) if x.cmd == "add" else rebuild()
