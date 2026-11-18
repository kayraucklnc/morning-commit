import html, json
E = html.escape

def fmt(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M".replace(".0M","M")
    if n >= 10_000: return f"{n/1000:.1f}k".replace(".0k","k")
    if n >= 1000: return f"{n:,}"
    return str(n)

def badge(likes=None, reposts=None, views=None, saves=None, extra=None):
    parts=[]
    if likes is not None: parts.append(f'<span class="b like">♥ {fmt(likes)}</span>')
    if reposts is not None: parts.append(f'<span class="b rt">⟲ {fmt(reposts)}</span>')
    if saves is not None: parts.append(f'<span class="b sv">🔖 {fmt(saves)}</span>')
    if views is not None: parts.append(f'<span class="b vw">👁 {fmt(views)}</span>')
    if extra: parts += [f'<span class="b ex">{E(x)}</span>' for x in extra]
    return '<div class="badges">'+''.join(parts)+'</div>'

def links(ls):
    return '<div class="links">'+' · '.join(f'<a href="{E(u)}">{E(t)}</a>' for t,u in ls)+'</div>'

def tryit(cmd):
    return f'<div class="tryit"><span>TRY IT</span><code>{E(cmd)}</code></div>' if cmd else ''

import re as _re

def hook_text(s, n=15):
    if s.get("hook"):
        return s["hook"]
    raw = _re.sub(r"<[^>]+>", "", " ".join(s.get("body") or [s.get("head") or ""]))
    words = raw.split()
    if not words:
        return s.get("head") or ""
    return " ".join(words[:n]) + ("…" if len(words) > n else "")

def card(s, cls="card"):
    img=""
    if s.get("gamma"):
        bands=''.join(f'<i style="background:rgb({int(i*255/31)},{int(i*255/31)},{int(i*255/31)})"></i>' for i in range(32))
        img=f'<figure class="gamma"><div class="band">{bands}</div><div class="smooth"></div><div class="glabel"><span>32 even steps (3dfx-style precision)</span><span>smooth</span></div></figure>'
    elif s.get("img"):
        inset=f'<img class="inset" src="{s["img2"]}" alt="">' if s.get("img2") else ''
        img=f'<figure><div class="ph"><img src="{s["img"]}" alt="">{inset}</div></figure>'
    cap = f'<figcaption>{E(s["cap"])}</figcaption>' if s.get("cap") else ''
    body='<div class="txt">'+''.join(f'<p>{p}</p>' for p in s.get("body") or [])+'</div>'
    hook=f'<p class="hook">{E(hook_text(s))}</p>'
    more=f'<details class="more"><summary>Read the story</summary>{cap}{body}{tryit(s.get("cmd"))}{links(s.get("links") or [])}</details>'
    return f'<article class="{cls}" id="{s["id"]}">{img}<div class="kicker">{E(s["kicker"])}</div><h3>{E(s["head"])}</h3>{hook}{badge(**s["b"])}{more}</article>'

def qh_html(items):
    return ''.join(f'<a class="qh" href="{E(u)}"><img src="{i}" alt=""><div><b>{E(h)}</b><p>{E(t)}</p><span>{E(sig)}</span></div></a>' for i,h,t,sig,u in items)

def liked_nav(items):
    if not items:
        return ''
    chips=[]
    for it in items:
        img=f'<img src="{E(it["img"])}" alt="">' if it.get("img") else ''
        extra=' chip-text' if not it.get("img") else ''
        href=it.get("href") or '#'
        chips.append(f'<a class="chip{extra}" href="{E(href)}">{img}<span class="chip-t">{E(it["title"])}</span><span class="chip-n">{E(it["n"])}</span></a>')
    return ('<nav class="liked" aria-label="Most-liked in the past 48 hours">'
            '<div class="liked-label">Most-liked, past 48h</div>'
            f'<div class="liked-track">{"".join(chips)}</div></nav>')

def section_cards(items):
    if not items:
        return ''
    out=[]
    for i,s in enumerate(items):
        if len(items)==1: cls='card full'
        elif i==0: cls='card wide'
        elif i==len(items)-1 and len(items)>=3: cls='card full'
        else: cls='card'
        out.append(card(s, cls))
    return '<div class="grid">'+''.join(out)+'</div>'

def optional_section(title, sid, items=None, intro=None, quicks=None, quicks_title=None):
    items = items or []
    quicks = quicks or []
    if not items and not quicks:
        return ''
    parts=[f'<div class="section" id="{sid}">{title}</div>']
    if intro:
        parts.append(f'<p class="wb-intro">{intro}</p>')
    if items:
        parts.append(section_cards(items))
    if quicks:
        if quicks_title:
            parts.append(f'<div class="section sub">{quicks_title}</div>')
        parts.append(f'<div class="qgrid">{qh_html(quicks)}</div>')
    return '\n'.join(parts)


stories = [
 dict(id="signudoc", kicker="Kill-your-SaaS weekend", img="img/signudoc-og.png", img2="img/kr-meme.jpg",
  cap="SignuDoc's own preview image. Inset: the meme @buccocapital posted on top of Kevin's post (4,460 likes).",
  head="Kevin Rose got an $8,100 DocuSign quote, so he built his own and gave it away",
  hook="Kevin Rose got an $8,100 DocuSign quote, so he built his own and gave it…",
  body=["Kevin Rose (he founded Digg) shared <b>SignuDoc</b>: a free e-signature app you deploy to your own Vercel account in one click. You upload a PDF, place signature fields, send links, and keep the sealed copy with an audit trail. There are no per-seat fees.",
        "It became <b>the biggest dev post of the past two days</b> because it's the purest example of a trend people keep joking about: when a SaaS bill feels too high, an AI coding agent builds you a replacement in a weekend. The top contributor on the repo is literally <i>claude</i>.",
        "<b>How to try it:</b> hit the Deploy button in the README. It sets up free Vercel, Neon (database) and Resend (email) plans, which the project says cover about 250 documents a month."],
  b=dict(likes=25277, reposts=1544, saves=13856, views=3384835),
  links=[("X post by @kevinrose","https://x.com/kevinrose/status/2122394902168473975"),("GitHub repo (MIT)","https://github.com/NYLLON-SOFTWARE/SignuDoc"),("The meme","https://x.com/buccocapital/status/2122452712948175000")],
  cmd=None),
 dict(id="allo", kicker="New toy for designers", img="img/allo-pop.jpg", img2="img/allo-og.png",
  cap="A frame from Josh's launch video, plus the font's preview card.",
  head="Allo, a free rounded font where you dial how friendly it looks",
  hook="Allo, a free rounded font where you dial how friendly it looks",
  body=["Designer Josh Puckett released <b>Allo</b>, a free, open-source font. It's a <i>variable</i> font, meaning one file holds a range of styles: you slide weight (100–900) and <b>roundness (0–100)</b> from sharp to fully round, and the letter shapes adjust for small or large text on their own.",
        "Designers loved it. The creator of Inter, the font half the web uses, called it <i>“a really nice ‘rounded Inter’.”</i> The <b>website is a toy in itself</b>, with live sliders.",
        "<b>Try it:</b> play with the sliders on the site, then drop it into your next landing page. It uses the SIL Open Font License."],
  b=dict(likes=8155, reposts=551, saves=8149, views=462400),
  links=[("X post by @joshpuckett","https://x.com/joshpuckett/status/2122329345670988258"),("allo.joshpuckett.me","https://allo.joshpuckett.me"),("GitHub","https://github.com/joshpuckett/allo")],
  cmd=None),
 dict(id="printer", kicker="Local AI, extreme edition", img="img/printer.jpg",
  cap="The printout from @osanseviero's post: Gemma's output, generated inside the printer.",
  head="Someone ran a Google AI model inside an office printer",
  hook="Someone ran a Google AI model inside an office printer",
  body=["Omar Sanseviero (he works on Google's Gemma models) turned a tiny 270M-parameter Gemma 3 model into a single <b>PostScript print job</b>. PostScript is the language printers use to draw pages, so the printer itself does the AI math.",
        "It used <b>14 MB of RAM</b> and took a <b>“blazing” 60 seconds per token</b>. It's useless and wonderful, and r/LocalLLaMA picked it up right away. He credits an AI coding helper called Carbon with building the engine."],
  b=dict(likes=577, reposts=30, saves=149, views=31781),
  links=[("X post by @osanseviero","https://x.com/osanseviero/status/2122646098418491739"),("r/LocalLLaMA thread","https://www.reddit.com/r/LocalLLaMA/comments/1xyjkts/gemma_on_a_printer/")],
  cmd=None),
 dict(id="ios", kicker="Viral demo", img="img/ios-web-frame.jpg",
  cap="Frame from the demo: several copies of Telegram's real iOS app, each running in a browser tab and each editable.",
  head="Telegram's real iPhone app, running in a browser tab with no iPhone and no emulator",
  hook="Telegram's real iPhone app, running in a browser tab with no iPhone and no emulator",
  body=["The team behind <b>Dessn</b> showed Telegram's actual iOS code (Swift and Objective-C) running in a web page through their own compiler and renderer, written in Rust. You can copy a screen, change it, and see the edit in under a second, much faster than an Xcode rebuild.",
        "It's a design tool: their goal is to turn <i>any</i> codebase into a canvas you can design on. iOS support is in closed beta, so for now it's mostly a jaw-drop demo to watch."],
  b=dict(likes=4450, reposts=263, saves=4067, views=304723),
  links=[("X post by @eminimnim","https://x.com/eminimnim/status/2122350451655864466"),("dessn.com","https://www.dessn.com")],
  cmd=None),
 dict(id="pybot", kicker="Weird experiment of the day", img="img/pybot-progress.png", img2="img/pybot-lines.jpg",
  cap="PyBot's progress chart: win rate climbing past the SmolLM-360M line as the codebase grows. Inset: the 636,549-line count from the launch video.",
  head="A chatbot with zero AI inside, written by 1,000 AI agents",
  hook="A chatbot with zero AI inside, written by 1,000 AI agents",
  body=["Hugging Face had a swarm of over 1,000 AI agents write a chatbot in <b>plain Python</b>: no neural network and no training, just if-statements, regexes and lookup tables, like a giant ELIZA.",
        "After more than 5,000 versions, <b>PyBot</b> grew to about 640k lines (plus 550k lines of tests) and <b>matches SmolLM-360M</b>, a real small language model, on their benchmark. It runs on a single CPU core, and when it says something dumb you can grep for the exact rule that did it."],
  b=dict(likes=2277, reposts=272, saves=1801, views=466564),
  links=[("X post by @lvwerra","https://x.com/lvwerra/status/2122335119750975925"),("GitHub","https://github.com/huggingface/pybot"),("Chat in browser","https://huggingface.co/spaces/HuggingFaceSwarms/PyBot")],
  cmd="git clone https://github.com/huggingface/pybot && cd pybot && python -m pybot"),
 dict(id="browse", kicker="Dev tool everyone's installing", img="img/browse-og.png",
  cap="OpenCode's preview card for Browse.",
  head="OpenCode Browse lets your coding agent drive your real browser",
  hook="OpenCode Browse lets your coding agent drive your real browser",
  body=["<b>Browse</b> is a Chrome extension plus an MCP server (MCP is the standard way to give AI agents tools). Your coding agent can open background tabs in <i>your</i> browser, with your logins, then click, type, take screenshots and record. When it hits a login, 2FA or payment step, it hands the tab back to you.",
        "Version 0.1 was rewritten in Rust: <b>25× less memory, 23× smaller, and no more Playwright</b>. It works with OpenCode, Claude Code, Cursor, Codex and Zed. It also hit the Hacker News front page (311 points)."],
  b=dict(likes=7263, reposts=287, saves=1923, views=317145, extra=["HN 311 pts"]),
  links=[("X post by @opencode","https://x.com/opencode/status/2122377687968678258"),("opencode.ai/product/browse","https://opencode.ai/product/browse"),("Source","https://github.com/anomalyco/browse")],
  cmd="Install the Chrome extension from opencode.ai/product/browse (it walks you through the CLI)"),
 dict(id="nanite", kicker="3D on the web", img="img/nanite-clusters.jpg", img2="img/nanite.jpg",
  cap="Meshes split into colour-coded triangle clusters (from the repo). Inset: the demo scene, 184M triangles with under 2M drawn.",
  head="Unreal Engine's famous “Nanite” trick, rebuilt for three.js",
  hook="Unreal Engine's famous 'Nanite' trick, rebuilt for three.js",
  body=["Nanite is the Unreal Engine feature that lets games use film-quality 3D models with millions of triangles. <b>three-nanite</b> brings the core idea to the browser: it cuts a model into small triangle clusters and draws each one only as detailed as it needs to look on screen.",
        "The demo scene has <b>184 million triangles but draws under 2 million</b> with no visible cracks or popping. The runtime is about 500 lines, it works with stock three.js materials, and it's MIT-licensed. The author says plainly that it's an experiment, not a production engine feature."],
  b=dict(likes=603, reposts=50, saves=517, views=22085),
  links=[("X post by @apekshik","https://x.com/apekshik/status/2122041787984613476"),("GitHub (MIT)","https://github.com/apekshik/three-nanite")],
  cmd="three-nanite build model.glb out/   # preprocess any GLB, see README"),
 dict(id="rex", kicker="Terminal nerds, rejoice", img="img/rex-demo.jpg", img2="img/rex-mitchell.jpg",
  cap="Stills from Mitchell Hashimoto's Rex demo: remote terminal sessions in the Rex app, and Mitchell explaining it.",
  head="The creator of Ghostty and Vagrant says remote dev finally feels local",
  hook="The creator of Ghostty and Vagrant says remote dev finally feels local",
  body=["Mitchell Hashimoto (he co-founded HashiCorp and made the Ghostty terminal) demoed <b>Rex</b>: one app that keeps your terminal sessions alive and reachable from any device, on your laptop or a remote server. In the demo, copy/paste, drag and drop and port forwarding just work across machines, and you can script it with Lua.",
        "<i>“Rex is done right. Rex is my answer, finally,”</i> he wrote about the “Vagrant for remote” request he's had for years. One early user said it replaced his Ghostty + tmux + Hammerspoon setup."],
  b=dict(likes=3338, reposts=162, saves=1779, views=169076),
  links=[("Demo by @mitchellh","https://x.com/mitchellh/status/2122464126240989217"),("“Done right” post","https://x.com/mitchellh/status/2122475070635622458"),("superlogical.com","https://www.superlogical.com")],
  cmd=None),
 dict(id="carmack", kicker="Thread worth your coffee", img=None, gamma=True,
  cap="Illustration made with CSS: the same black-to-white ramp with 32 levels spread evenly (top) versus smooth (bottom). See how the dark end bands?",
  head="John Carmack explains why old 3dfx graphics cards looked washed out",
  hook="John Carmack explains why old 3dfx graphics cards looked washed out",
  body=["The Doom and Quake programmer wrote a mini-essay on <b>gamma</b>. 3dfx cards treated pixel brightness as linear, so 1.0 is twice as bright as 0.5. That's correct maths, but with only 5–6 bits per colour it spends precision on brights your eye barely notices and leaves <b>harsh bands in the darks</b>.",
        "On top of that, artists painted textures on normal, non-linear monitors, which is where the famous faded glQuake look came from. <i>“Even today, tons of games don't properly handle gamma.”</i> It's a five-minute read that makes colour spaces finally click."],
  b=dict(likes=5533, reposts=428, saves=1203, views=152180, extra=["HN 241 pts"]),
  links=[("X post by @ID_AA_Carmack","https://x.com/ID_AA_Carmack/status/2122478083319992513")],
  cmd=None),
 dict(id="sensenova", kicker="New local model", img="img/sensenova.jpg",
  cap="Benchmark chart shared in @cheatyyyy's post (vendor numbers).",
  head="A 9B “looped” model that claims to punch like a 27B, with open weights",
  hook="A 9B 'looped' model that claims to punch like a 27B, with open weights",
  body=["SenseTime released <b>SenseNova-Loop-9B</b> under the Apache 2.0 license. The trick: it stores 32 layers but runs 24 of them twice, so a small model does the work of a much deeper one. That means more brains for the same VRAM.",
        "Their benchmarks put it level with Qwen 3.8-27B, and r/LocalLLaMA is excited. Treat those as vendor claims until people test it. One tester estimates about 15 GB of VRAM for a 256k context, and GGUF builds for llama.cpp, Ollama and LM Studio are promised soon."],
  b=dict(likes=488, reposts=22, saves=312, views=16665),
  links=[("X post by @cheatyyyy","https://x.com/cheatyyyy/status/2122675785530269932"),("Hugging Face","https://huggingface.co/sensenova/SenseNova-Loop-9B"),("r/LocalLLaMA","https://www.reddit.com/r/LocalLLaMA/comments/1xymz9z/sensenovaloop9b_vs_its_own_preview/")],
  cmd=None),
 dict(id="unsloth", kicker="Local AI agents", img="img/unsloth-gimp.jpg",
  cap="Frame from Unsloth's demo: a local Qwen model built this expense report on its own.",
  head="Your local model can now use your computer's apps",
  hook="Your local model can now use your computer's apps",
  body=["<b>Unsloth</b>, a popular tool for running and fine-tuning models at home, added beta “computer use” for <i>any</i> local model. In the demo, Qwen3.8-27B running locally turned receipts into an expense report and used GIMP to resize photos and add captions. They also added control of Blender and Unreal Engine."],
  b=dict(likes=290, reposts=36, saves=119, views=10716),
  links=[("X post by @danielhanchen","https://x.com/danielhanchen/status/2122365870995612059"),("Release notes","https://github.com/unslothai/unsloth/releases/tag/v0.1.918-beta")],
  cmd=None),
]

quick = [
 ("img/t3-omarchy.jpg","T3 Code lets you re-skin the app by asking your agent","Theo's open-source agent app now restyles itself live from a prompt, and people are posting their themes.","@theo, 5,231 ♥","https://x.com/theo/status/2121455838414201200"),
 ("img/antigravity-fps.jpg","20+ agents built a 3D shooter in the browser from one prompt","A stress test of Google Antigravity's new /swarm mode, with no external 3D models, textures or audio.","@vamsibatchuk, 432 ♥","https://x.com/vamsibatchuk/status/2122509308797579477"),
 ("img/nfsu2.jpg","Need for Speed Underground 2, reimplemented in Rust","Overbright v0.2 adds 4K, 240 FPS and ray-traced wet streets. You need your own copy of the game.","@McGroin83, 223 ♥","https://x.com/McGroin83/status/2122335930098852056"),
 ("img/chlobe.jpg","chlobe: a 15 KB spinning globe with country borders","A fork of the tiny cobe shader globe that can show country data. Great for dashboards.","@lachlanjc, 50 ♥","https://x.com/lachlanjc/status/2122461709638283462"),
 ("img/frame-og.jpg","Frame: a 31.5-inch colour e-paper display","TRMNL's giant e-ink screen for calm dashboards hit the Hacker News front page.","HN, 497 pts","https://trmnl.com/blog/introducing-frame"),
 ("img/nemotron.jpg","NVIDIA's diffusion language models","Nemotron-Labs-Sigma (3B and 8B) writes text by denoising, like image models do, instead of one token at a time.","@MardaniMorteza, 157 ♥","https://x.com/MardaniMorteza/status/2122392994188079562"),
 ("img/gh_meta_astryx.png","meta/astryx is exploding on GitHub","Meta's open-source, “agent-ready” design system gained 10,939 stars this week.","GitHub trending","https://github.com/meta/astryx"),
 ("img/gh_jingyaogong_minimind.png","Train your own 64M-parameter LLM in 2 hours","minimind is back on GitHub trending, a great weekend project for learning how LLMs work.","GitHub trending, +188★ today","https://github.com/jingyaogong/minimind"),
]

# ===================== WORKBENCH: HARDWARE & DIY (REQUIRED in every edition since 2026-11-17) =====================
# Kayra asked for MORE stories and especially hardware/DIY. Every edition must fill:
#   hw[]      5-7 full cards (same dict shape as stories[]); first one is rendered "card wide",
#             the last one "card full" (see the Workbench block in the TEMPLATE). Put a real BOM / repo /
#             kit in `cmd` (rendered as a TRY IT box) or in a "Build it:" paragraph.
#   hwquick[] 8-12 hardware quick hits (img, head, text, signal, url)
#   swquick[] 3-5 extra software/creative quick hits (appended to quick[])
# Total target: about 15-20 items beyond the lead, never padded with weak items.
hw = [
 dict(id="flipper", kicker="Hacker gadget of the year?", img="img/flipper-ks.jpg", img2="img/flipper-2.jpg",
  cap="Flipper One's product shot from the Kickstarter page. Inset: Flipper's launch image of it plugged into a desk setup.",
  head="Flipper One, the Flipper Zero team's pocket Linux computer, raised about $6M in two and a half hours",
  hook="Flipper One, the Flipper Zero team's pocket Linux computer, raised about $6M in two and…",
  body=["The people behind <b>Flipper Zero</b> (the orange dolphin gadget for poking at radios, NFC and infrared) launched their next device on Kickstarter at 17:00 Rome time. <b>Flipper One</b> isn't a radio toy. It's a pocket <b>network multi-tool</b> that runs full Linux (Debian-based Flipper OS) on an 8-core Rockchip RK3576, with a Raspberry Pi RP2350 microcontroller running the screen and buttons even when Linux is off.",
        "What it does: Wi-Fi 6E, gigabit Ethernet and eSIM, up to five internet uplinks with failover, hotspot/VPN/firewall, network scanning, and an internal M.2 slot for 5G modems, SDR radios or an NVMe drive. One USB-C cable gives you SSH, a serial console and charging. Flipper says it runs a mainline Linux kernel and that it's working with Collabora to upstream the chip support.",
        "<b>The numbers:</b> by 19:24 Rome time the campaign showed <b>$5,993,578 from 11,884 backers</b>. Rewards start at <b>$399</b>; per the campaign details shared on X, it runs until December 17 and shipping is estimated for <b>July 2027</b>."],
  b=dict(likes=593, reposts=80, saves=108, views=24048, extra=["$5.99M pledged","11,884 backers"]),
  links=[("Kickstarter","https://www.kickstarter.com/projects/flipper-devices/flipper-one"),("Launch post by @flipper_net","https://x.com/flipper_net/status/2122721732817502296"),("Spec rundown by @sysxplore","https://x.com/sysxplore/status/2122728535403938032"),("HN thread","https://news.ycombinator.com/item?id=50533312")],
  cmd=None),
 dict(id="atomdog", kicker="Cute robot of the day", img="img/atomdog-1.jpg", img2="img/atomdog-2.jpg",
  cap="AtomDog from M5Stack's post. Inset: the parts before assembly: four micro servos, the ATOM board and the printed body.",
  head="AtomDog: a palm-sized robot dog you can 3D print and control from your browser",
  hook="AtomDog: a palm-sized robot dog you can 3D print and control from your browser",
  body=["M5Stack spotlighted <b>AtomDog</b>, a tiny four-legged robot by maker se kino. It walks, sits, waves a paw and “barks”, and you calibrate and drive it from a <b>web page the robot serves itself</b> (open <code>dogrobot.local</code>), so there's no app to install.",
        "It's a very friendly first robot: only <b>four servos</b>, one per leg, and the gait (step size, speed, centre of gravity) is tuned with sliders in real time. Everything is MIT-licensed: firmware, 3D models and PCB data.",
        "<b>Build it:</b> M5Stack ATOM Lite (ESP32) + ATOMIC Motion Base + 4× Feetech FS90MG micro servos + seven PLA prints. Flash it with PlatformIO; the project page lists every step."],
  b=dict(likes=393, reposts=66, saves=165, views=14931),
  links=[("X post by @M5Stack","https://x.com/M5Stack/status/2122575269181722778"),("Build guide + files (Hackster)","https://www.hackster.io/kinosei/atomdog-open-source-quadruped-robot-with-m5atommotion-aa540d")],
  cmd="BOM: ATOM Lite + ATOMIC Motion Base + 4× FS90MG servos + PLA"),
 dict(id="tinyeng", kicker="Give your coding agent a body", img="img/tinyeng-robot.jpg", img2="img/autonomous-lamp.jpg",
  cap="Tiny Engineer at its desk (frame from the demo video). Inset: the “Autonomous Lamp”, another agent-powered desk robot going around this week.",
  head="Tiny Engineer: a desk robot that acts out what Claude Code or Cursor is doing",
  hook="Tiny Engineer: a desk robot that acts out what Claude Code or Cursor is doing",
  body=["<b>Tiny Engineer</b> is a little open-source robot that sits next to your monitor and mirrors your AI agent. It looks around while the agent reads files, types on its tiny laptop while it writes code, stares at the ceiling while it thinks, and <b>rings a bell when the task is done</b>. It's a progress bar you can actually watch.",
        "Inside, an ESP32 gets activity signals over Wi-Fi and turns them into servo moves, OLED faces and sounds. The repo has <b>1,191 GitHub stars</b>. The maker rates it “a fair first hardware project for a software engineer.” In the same vein, a 3D-printed Pixar-style <b>Autonomous Lamp</b> with five servos, a camera and a mic was making the rounds; its post says the software is open source.",
        "<b>Build it:</b> 5× SG90 servos, an ESP32, an OLED, a small speaker and the open-source control board (KiCad files included), plus prints and M2 screws. Then hook it up to your agent:"],
  b=dict(likes=15, reposts=3, saves=12, views=766, extra=["1,191★ on GitHub","Lamp post ♥ 56"]),
  links=[("GitHub: jamro/tiny-engineer","https://github.com/jamro/tiny-engineer"),("Demo video","https://youtu.be/RX_QRxdXMjg"),("Post by @Psalteric","https://x.com/Psalteric/status/2122139766065877477"),("Autonomous Lamp post","https://x.com/Psalteric/status/2122447224395436521")],
  cmd="npx -y tiny-engineer setup"),
 dict(id="alive", kicker="Robots as film stars", img="img/almost-alive-frame.jpg",
  cap="Frame from “Almost Alive”: three 3D-printed SO-101 arms keep an orange ball moving through a purple track.",
  head="A tiny nature documentary starring three flawed robot arms",
  hook="A tiny nature documentary starring three flawed robot arms",
  body=["<i>“One can't see, one can't think, one overthinks everything!”</i> <b>Almost Alive</b> is a gorgeous 4½-minute short shot on camera (not rendered) by @pbshgthm, @amey_sharma and @harshitsatija, narrated like a wildlife film. Three robot arms pass an orange ball around a looping track and, together, almost seem alive.",
        "The arms are <b>SO-101s</b>, the cheap open-source arm everyone in hobby robotics is printing right now, trained with Hugging Face's <b>LeRobot</b>. The team printed the parts and taught the arms by hand.",
        "<b>Build your own arm:</b> the SO-101 design (Apache-2.0, 8,151★) has the parts list and print files, and LeRobot has the tutorials for teaching it by demonstration."],
  b=dict(likes=148, reposts=44, saves=22, views=9291),
  links=[("Watch it (X)","https://x.com/pbshgthm/status/2122679067065598015"),("SO-101 arm files","https://github.com/TheRobotStudio/SO-ARM100"),("LeRobot","https://github.com/huggingface/lerobot")],
  cmd=None),
 dict(id="pager", kicker="E-paper weekend build", img="img/pager.jpg",
  cap="The $24 desk pager: “3 agents waiting on you”, on a tiny e-ink screen.",
  head="A $24 e-ink “pager” that tells you when your AI agents need you",
  hook="A $24 e-ink 'pager' that tells you when your AI agents need you",
  body=["Vipul Gupta built a <b>pocket-sized e-ink desk pager</b> from a Raspberry Pi Zero. It shows three things: AI agent notifications, how much of his usage limits he's burned, and texts from his girlfriend. <i>“No phones. No pings.”</i> Adafruit picked it up on their blog.",
        "The idea is the point: a calm, single-purpose screen beats a phone full of notifications. He hasn't published a repo as far as we can see, so treat it as a recipe: <b>Pi Zero 2 W + a small SPI e-paper display</b>, and a script that polls whatever you care about."],
  b=dict(likes=125, reposts=10, saves=56, views=22162),
  links=[("X post by @vipulgupta2048","https://x.com/vipulgupta2048/status/2122305000194158709"),("Adafruit blog","https://blog.adafruit.com/2026/11/16/a-24-e-ink-desk-pager-built-from-a-raspberry-pi-zero/")],
  cmd=None),
 dict(id="framework", kicker="Keyboards", img="img/fw-1.jpg", img2="img/fw-3.jpg",
  cap="Framework's launch photos: the keyboard in a living room, and the translucent back that shows the internals.",
  head="Framework's hackable wireless keyboard has open firmware and a control board you can buy on its own",
  hook="Framework's hackable wireless keyboard has open firmware and a control board you can buy on…",
  body=["Framework (the repairable-laptop company) opened pre-orders for its <b>Wireless Touchpad Keyboard</b>, a slim keyboard-plus-touchpad meant for the couch, servers, Raspberry Pis and sim rigs. Framework says it's the biggest waitlist it has ever had, and 40 minutes later it posted that pre-order batches were <i>“selling through extremely quickly.”</i>",
        "The maker angle: the firmware is an open-source <b>fork of ZMK</b> (remap with ZMK Studio), the <b>control board</b> (Nordic nRF54LM20A with a 0.1″ header) will be sold separately so you can build your own keyboards around it, and there's <b>open surface CAD</b> for 3D-printing mounts. The battery is replaceable, and it runs on the Framework Laptop 12 keyboard module with a 120 Hz PixArt touchpad and 8 kHz wired polling.",
        "<b>How to get it:</b> a fully refundable $50 deposit; the first batches ship in Q1 2027 with a US ANSI layout. Framework didn't list the final price in its post."],
  b=dict(likes=472, reposts=23, saves=58, views=19205),
  links=[("Framework blog","https://frame.work/blog/pre-orders-open-for-framework-wireless-touchpad-keyboard"),("X post by @FrameworkPuter","https://x.com/FrameworkPuter/status/2122729045695816052"),("“Selling through” update","https://x.com/FrameworkPuter/status/2122739182795968787")],
  cmd=None),
]

hwquick = [
 ("img/pixelclock.jpg","PixelClock: an LED clock with no soldering","One 2.5 m WS2812B strip woven through a 3D-printed frame makes a 7×19 pixel display. ESP32, web setup, flash it from the browser.","Hackaday · free on Printables","https://www.printables.com/model/1703397-pixelclock"),
 ("img/artmatrix.jpg","Pimoroni Art Matrix: 16,384 pixels on your wall","A framed 128×128 RGB LED panel driven by an RP2350, with 45 art, weather and retro-screensaver plugins. All MicroPython. £159.","@pimoroni, 47 ♥","https://shop.pimoroni.com/products/artmatrix"),
 ("img/iris.jpg","IRis: an open-source universal remote","ESP32, a 1.3″ OLED, an IR receiver and two IR LEDs in a printed case. It learns codes from your old remotes and replays them.","@Hacksterio, 26 ♥ · 22 🔖","https://www.hackster.io/news/give-your-old-remotes-the-boot-with-iris-846fc253a8e5"),
 ("img/koshiro.jpg","A budget robot dog, with 12 home-made motors","Koshiro Robot Creator designed his own quasi-direct-drive brushless actuators with custom FOC boards instead of buying pricey ones.","Hackster","https://www.hackster.io/news/giving-a-robot-dog-some-muscle-9e96b4682183"),
 ("img/manga.jpg","A giant Tamagotchi that reads manga","Arnov Sharma put a Waveshare ESP32-P4 4.3″ touchscreen in a printed Tamagotchi shell. Load manga from an SD card and swipe through it.","Hackster · full build guide","https://www.hackster.io/Arnov_Sharma_makes/mega-tamagotchi-manga-reader-8cf8ba"),
 ("img/wesbos.jpg","Wes Bos turned a conference badge into a photo booth","Burned out on AI coding, he added a camera and a thermal printer to his RP2350 GitHub Universe badge.","Hackster","https://www.hackster.io/news/this-conference-badge-is-now-a-tiny-photo-booth-bcbb945ab028"),
 ("img/pi5-survival.jpg","A Raspberry Pi 5 survival computer, 24+ hours on battery","Offline Wikipedia, world maps, GPS and SDR radio in a printed case with a 256 Wh LiFePO4 pack. Lastbook's hardware cousin.","@0x0SojalSec, 26 ♥","https://x.com/0x0SojalSec/status/2122467597556060318"),
 ("img/eink-ipod.jpg","An e-ink iPod, built with AI help","David Feldt says he made a working e-ink music player without writing code or drawing CAD, using Blueprint to prototype it.","@davidfeldt, 119 ♥","https://x.com/davidfeldt/status/2122029433192329361"),
 ("img/deskbot.jpg","A cute ESP32-S3 desk buddy with its own app","Seun built a little red desk robot: Arduino IDE for the ESP32-S3, a 3D-printed body and a Flutter phone app.","@seunmolz, 72 ♥","https://x.com/seunmolz/status/2122047166395117891"),
 ("img/fm1.jpg","A cheap FM-1 toy synth got hacked wide open","A DX7-clone toy synth became the hot hacking platform; the community's work pushed the maker to release an open SDK.","Hackaday feature","https://hackaday.com/2026/11/17/the-fm-1-open-source-hacked-open-vibe-coding-and-farting-synthesizers/"),
 ("img/rigol.png","Custom Linux firmware for Rigol DHO scopes","OOS runs from the scope's SD card next to the stock OS, on a Linux 6.12 kernel, written in Rust. Early days: tested on a couple of models.","Hackaday · 134★","https://github.com/dekajoule/oos"),
 ("img/arcane.png","Arcane: a friendly web UI for your homelab's Docker","Manage containers, images and stacks from the browser. BSD-licensed, 9,192 stars total.","GitHub trending, +654★ today","https://github.com/getarcaneapp/arcane"),
]

swquick = [
 ("img/threejs-sponza.webp","Building a AAA lighting pipeline in three.js","Ben Houston maps every stage games use (lightmaps, probes, SSR) against three.js, with links to the PRs that close the gaps.","HN, 153 pts","https://ben3d.ca/blog/building-the-aaa-lighting-pipeline-in-threejs"),
 ("img/squircle.png","Squircles, explained with live sliders","Linebender's wiki page on the shape between a square and a circle, with an interactive tester comparing every variant.","HN, 218 pts","https://linebender.org/wiki/curves/squircle/"),
 ("img/vbworld.png","VisualBasic.World: 15 years of VB programs","A browsable gallery of Planet Source Code programs from 1997–2012. Pure nostalgia.","HN, 179 pts","https://visualbasic.world/"),
 ("img/alloy.png","Alloy CSS: dialogs, menus and tabs with JavaScript off","A Show HN for a CSS/HTML kit whose interactive components keep working without JS.","Show HN, 106 pts","https://alloyhtml.com/example.html"),
]

quick = quick + swquick

# Optional sections: leave a list empty to omit it. Never pad.
security = []
tips = []
games = []

numbers = [("SignuDoc",25277),("Lastbook",15550),("Allo font",8155),("OpenCode Browse",7263),("Carmack on gamma",5533),("iOS in the browser",4450),("Rex",3338),("PyBot",2277),("three-nanite",603),("Gemma in a printer",577)]


# Optional sections must exist (leave empty to omit them from the page).
security = security if "security" in dir() else []
tips = tips if "tips" in dir() else []
games = games if "games" in dir() else []

S={s["id"]:s for s in stories+hw+security+tips+games}
hwqh=qh_html(hwquick)
maxn=max(n for _,n in numbers)
bars=''.join(f'<div class="bar"><span class="bl">{E(k)}</span><span class="bt"><i style="width:{n/maxn*100:.1f}%"></i></span><span class="bn">{n:,}</span></div>' for k,n in numbers)
qh=qh_html(quick)

ticker=" ◆ ".join(["Flipper One: ~$6M on Kickstarter in 2.5 hours","SignuDoc ♥ 25.3k","Lastbook ♥ 15.5k · 100 TB downloaded in a day","Allo ♥ 8.2k","OpenCode Browse ♥ 7.3k","Carmack ♥ 5.5k","iOS-in-a-tab ♥ 4.5k"])

# Phone-only chip strip. Each item: short title, like/stat, image, href to #id or a URL.
liked = [
 dict(title="SignuDoc", n="♥ 25.3k", img="img/signudoc-og.png", href="#signudoc"),
 dict(title="Lastbook", n="♥ 15.5k · 100 TB", img="img/lastbook-og.png", href="#lastbook"),
 dict(title="Allo", n="♥ 8.2k", img="img/allo-pop.jpg", href="#allo"),
 dict(title="OpenCode Browse", n="♥ 7.3k", href="#browse"),
 dict(title="Carmack", n="♥ 5.5k", href="#carmack"),
 dict(title="iOS-in-a-tab", n="♥ 4.5k", href="#ios"),
]
liked_html = liked_nav(liked)
sec_html = optional_section("Security", "security", security)
tips_html = optional_section("Tips", "tips", tips)
games_html = optional_section("Game mechanics", "games", games, intro="Indie and procedural ideas where the mechanic is the story.")
wb_html = optional_section("Workbench: Hardware &amp; DIY", "workbench", hw,
    intro="Robots, gadgets and weekend builds makers were sharing in the past 48 hours, each with what you'd need to build or try it.",
    quicks=hwquick, quicks_title="More from the workbench")
qh_block = ('<div class="section">Quick hits</div><div class="qgrid">'+qh+'</div>') if quick else ''



# ===================== TEMPLATE (keep this part; edit story data above) =====================
# Shared newspaper CSS lives in the site repo at /assets/style.css (linked as ../../assets/style.css).
# Only put edition-specific tweaks (per-story #id rules) in EDITION_CSS.
# tools/sitegen.py injects the PWA head tags, prev/next nav and footer nav when publishing.
# Every story needs a short `hook` (about 15 words) for the phone layout.
# Security, Tips, Game mechanics and Workbench are all optional: leave a list empty
# and that section is omitted. Never pad a section.
import sys, os, shutil
OUT = sys.argv[1] if len(sys.argv) > 1 else "/workspace/digest/out/2026-11-17"
IMG_SRC = sys.argv[2] if len(sys.argv) > 2 else "/workspace/digest/v3/allimg"
DATE_LONG = "Tuesday, November 17, 2026"
VOL = "Vol. I · No. 2"
EDITION_CSS = """
.wb-intro{text-align:center;font-style:italic;margin:-8px auto 22px;max-width:640px}
.section.sub{font-size:22px;margin-top:34px}
#workbench{scroll-margin-top:12px}
#atomdog .ph>img:first-child,#pager .ph>img:first-child{aspect-ratio:4/3.4;object-position:center 45%}
#flipper .ph>img:first-child{object-fit:contain;background:#fff}

#printer .ph>img:first-child{aspect-ratio:4/5;object-position:center 60%}
#pybot .ph>img:first-child,#sensenova .ph>img:first-child{object-fit:contain;background:#fff}
#signudoc .ph .inset{width:26%;bottom:-30px}
@media (max-width:760px){#signudoc .ph .inset{width:30%;bottom:-22px}#printer .ph>img:first-child{aspect-ratio:4/4.4}}
"""
LEAD_HEAD = "Lastbook, the free offline “rebuild society” library, broke the internet's download counter"
LEAD_HOOK = "A free offline library of guides, maps and a local AI, and it blew past 100 TB of downloads."
LEAD_DECK = "A free desktop app that packs survival guides, maps, how-to videos and a local AI chatbot. Once it's downloaded, it all works with the internet off."

page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>The Morning Commit, {DATE_LONG}</title>
<meta name="description" content="{E(LEAD_DECK)}">
<meta name="mc:lead" content="{E(LEAD_HEAD)}">
<meta name="mc:deck" content="{E(LEAD_DECK)}">
<meta name="mc:thumb" content="img/lastbook-og.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=Inter:wght@500;700;800&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/style.css">
<style>{EDITION_CSS}</style>
</head>
<body><div class="paper">
<div class="topline"><span>{VOL}</span><span>{DATE_LONG} · Rome edition</span><span>What blew up on X, HN, GitHub &amp; the workbench</span></div>
<header class="mast"><h1>The Morning Commit</h1><div class="tag">The things builders were playing with while you weren't scrolling</div></header>
<div class="ticker"><b>MOST-LIKED, PAST 48H ▸</b>{E(ticker)}</div>
{liked_html}

<section class="lead" id="lastbook">
 <div>
  <figure class="hero"><img class="main" src="img/lastbook-og.png" alt="Lastbook"><img class="chart" src="img/lastbook-100tb.jpg" alt="Lastbook downloads chart"><figcaption>Lastbook's launch card. Pinned: the chart @farbood posted with the “100TB downloaded today” update: 131.2 TB in 74.5 hours since launch, and look at that spike after the viral post.</figcaption></figure>
  <div class="kicker">Lead story · Local AI meets doomsday prep</div>
  <h2>{E(LEAD_HEAD)}</h2>
  <p class="hook">{E(LEAD_HOOK)}</p>
  <p class="deck">{E(LEAD_DECK)}</p>
  {badge(likes=15550, reposts=1122, saves=32943, views=2423990, extra=["8.2 TB in 31 min","100 TB in a day"])}
  <details class="more lead-more">
  <summary>Read the story</summary>
  <div class="cols">
   <p>Lastbook bundles thousands of practical guides (first aid, safe water, food preservation, repairs, solar power), <b>258,000+ searchable places</b> on offline maps (water, fire stations, shelters) and <b>2,324 videos</b>. You can also ask a <b>local Gemma 4 model</b> questions, and it answers from the library and links its sources. Nothing leaves your machine.</p>
   <p>Why it went viral: the launch post's <b>bookmarks (32.9k) outnumbered its likes</b>, the classic sign of “I'm saving this for later.” Then came the follow-ups: <i>“8.2 TB downloaded in the last 31 minutes”</i> and <i>“100TB downloaded today.”</i> It's open source, so people are already talking about loading it onto old tablets with solar chargers.</p>
   <p><b>Try it tonight:</b> it runs on Mac (Apple Silicon), Windows and Linux. Pick Small (7.7 GB), Medium (67.5 GB) or All (about 388 GB); the local AI adds about 17 GB. The medical content comes from published guides (Hesperian, WHO, Red Cross), and the site notes it isn't clinically reviewed.</p>
  </div>
  {links([("X post by @farbood","https://x.com/farbood/status/2122413856693858581"),("“8.2 TB in 31 minutes”","https://x.com/farbood/status/2122449011886244058"),("lastbook.org","https://lastbook.org"),("GitHub","https://github.com/Immortal-Protocols/lastbook")])}
  </details>
 </div>
 <aside class="side">
  <details class="more side-more">
  <summary>Try it tonight</summary>
  <div class="boxh">Try it tonight</div>
  <div class="try"><ul>
   <li><b>Chat with a bot that has no AI</b><code>git clone https://github.com/huggingface/pybot
cd pybot &amp;&amp; python -m pybot</code><small>Python 3.8+, nothing else to install.</small></li>
   <li><b>Let your agent use your real browser</b><code>curl -fsSL https://opencode.ai/browse/install | bash</code><small>Install the Chrome extension first; it guides you.</small></li>
   <li><b>Play with a squishy font</b><code>allo.joshpuckett.me</code><small>Drag the roundness slider. Free under the OFL.</small></li>
   <li><b>Billions of triangles in three.js</b><code>three-nanite build model.glb out/</code><small>Grab the repo: github.com/apekshik/three-nanite</small></li>
   <li><b>Give your agent a desk robot</b><code>npx -y tiny-engineer setup</code><small>After you build the ESP32 bot: github.com/jamro/tiny-engineer</small></li>
   <li><b>A survival library with offline AI</b><code>lastbook.org → Download</code><small>Small pack is 7.7 GB; local AI adds about 17 GB.</small></li>
  </ul></div>
  <div class="numbers"><div class="boxh">By the numbers · likes on X</div>{bars}<div class="src">Likes on each story's main X post, read via the X API on Nov 17, around 17:40 Rome time (UTC+1).</div></div>
  </details>
 </aside>
</section>

<div class="section">Today's feed</div>
<div class="grid">
 {card(S["signudoc"],"card wide")}
 {card(S["printer"])}
 {card(S["allo"])}
 {card(S["ios"])}
 {card(S["browse"])}
</div>

<details class="more quotes-more">
 <summary>Quotes from today</summary>
<div class="pull">
 <blockquote>The great AI degrifting has begun.<cite>@tunguz, quoting Kevin Rose's SignuDoc post · 7,260 ♥ · <a href="https://x.com/tunguz/status/2122437479756407215">post</a></cite></blockquote>
 <blockquote>A new era of software is upon us. Personalized, fully owned, open source.<cite>@rauchg (Vercel CEO) · 4,555 ♥ · <a href="https://x.com/rauchg/status/2122396034186014919">post</a></cite></blockquote>
 <blockquote>Rex killed my entire setup: Ghostty, Tmux, Hammerspoon… It really is magic.<cite>@elijahmuraoka_ · 500 ♥ · <a href="https://x.com/elijahmuraoka_/status/2122472094588121234">post</a></cite></blockquote>
</div>
</details>

<div class="grid" style="margin-top:26px">
 {card(S["pybot"],"card wide")}
 {card(S["carmack"])}
 {card(S["nanite"])}
 {card(S["rex"])}
 {card(S["sensenova"])}
 {card(S["unsloth"],"card full")}
</div>

{sec_html}
{tips_html}
{games_html}
{wb_html}
{qh_block}

<footer><div><b>How this edition was made:</b> we searched X for stories developers were sharing and posts from local-AI and creative-coding accounts in the last 48 hours, ranked them by real engagement, and cross-checked against GitHub Trending, the Hacker News front page and r/LocalLLaMA. The Workbench section adds maker accounts on X (M5Stack, Adafruit, Pimoroni, Hackster, Flipper, Framework), Hackaday, Hackster.io and Kickstarter. Numbers for the original stories come from about 17:40 Rome time (UTC+1) on Nov 17, and for the Workbench and the later quick hits from about 19:20. Benchmarks and claims belong to their authors.</div><div style="min-width:260px;text-align:right"><b>The Morning Commit</b><br>Assembled for Kayra by Grok Bot<br>Tomorrow's edition lands by 8:00 (Rome)</div></footer>
</div></body></html>'''
os.makedirs(OUT + "/img", exist_ok=True)
open(OUT + "/index.html", "w").write(page)
for f in os.listdir(IMG_SRC):
    if f"img/{f}" in page: shutil.copy2(os.path.join(IMG_SRC, f), OUT + "/img/" + f)
print("wrote", OUT + "/index.html", len(page), "bytes")
