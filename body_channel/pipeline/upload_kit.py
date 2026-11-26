"""Write episodes/<ep>/UPLOAD.md (title, description with chapters + sources, tags, pinned comment, schedule),
episodes/<ep>/<ep>.srt and scripts/<ep>_script.md (readable script + sources + fact-check).
Usage: python3 pipeline/upload_kit.py ep01 out/EP01.times.json"""
import json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vfilm import parse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHANNEL = "Your Vitals"
META = {
 "ep01": dict(title="What Happens to Your Body If You Stay Awake for 11 Days", date="Wednesday 2 December 2026",
   hook="Day 11. No sleep for 264 hours. Your brain is switching off in patches, and you can't even tell.",
   blurb="In 1963 a 17-year-old in San Diego stayed awake for 11 days and 25 minutes for a school science fair. We relive it as YOU, hour by hour, with a live vitals monitor: the point where your brain performs like it's drunk (17 hours), microsleeps, hallucinations, what sleep loss does to rats and fruit flies, and the price Randy Gardner paid years later.",
   tags="what happens to your body if, stay awake for 11 days, randy gardner, sleep deprivation, no sleep, what happens if you don't sleep, microsleep, sleep science, human body, body science, your vitals, science explained",
   comment="Longest you've ever stayed awake? Be honest 👇 (Randy's record: 264 hours.)",
   shorts=["17 hours awake = your brain on 0.05% alcohol. #sleep #science", "This teen stayed awake for 11 days. Here's what it did to him. #science #body"]),
 "ep02": dict(title="What Happens to Your Body If You Fall Into the Mariana Trench", date="Wednesday 9 December 2026",
   hook="11 kilometres of water, 1,100 times surface pressure, and you're still not flat. Here's why.",
   blurb="A science thought experiment: you fall in above the Challenger Deep and we follow your body all the way down, depth by depth. The diving reflex, the squeeze on your ears and lungs, the deepest a human has ever gone, the last sunlight, the deepest fish on Earth, and who's waiting for you at the bottom.",
   tags="what happens to your body if, mariana trench, challenger deep, deep sea, ocean pressure, what if you fell into the mariana trench, deep ocean, snailfish, trieste, body science, your vitals, science explained",
   comment="At what depth would YOU have started panicking? 👇",
   shorts=["Why the deep sea doesn't crush you into a cube. #ocean #science", "No fish lives below ~8,200 m. Here's why. #marianatrench #science"]),
 "ep03": dict(title="What Happens to Your Body If You Get Struck by Lightning", date="Wednesday 16 December 2026",
   hook="300 million volts, and 9 in 10 people survive. That's not the good news you think it is.",
   blurb="A direct lightning strike, second by second: flashover across your skin, a heart that stops and restarts by itself, breathing that doesn't, temporary paralysis, fern-shaped 'lightning tattoos', and the invisible brain injury many survivors live with. Plus Roy Sullivan, the park ranger struck seven times.",
   tags="what happens to your body if, struck by lightning, lightning strike, lightning survivor, roy sullivan, lichtenberg figure, lightning safety, human body, body science, your vitals, science explained",
   comment="Have you (or someone you know) ever been close to a lightning strike? 👇",
   shorts=["Lightning gives you a tattoo… then takes it back. #lightning #science", "This man was struck by lightning 7 times. #science #weird"]),
 "ep04": dict(title="What Happens to Your Body If You Eat Only Fast Food for 30 Days", date="Wednesday 23 December 2026",
   hook="Your liver sounds the alarm in under 4 weeks. The scariest result shows up a year after you stop.",
   blurb="Super Size Me made it famous, but a controlled Swedish study did it properly: 18 healthy young adults, two-plus fast food meals a day, no exercise, weekly blood tests, and a follow-up 2.5 years later. Day by day: your arteries after one meal, your gut bacteria, your liver enzymes, and the souvenir that stays.",
   tags="what happens to your body if, fast food for 30 days, super size me, eating fast food every day, liver, gut microbiome, ultra processed food, nutrition science, human body, body science, your vitals, science explained",
   comment="Next month YOU pick the episode. What should your body survive next? Most-liked comment wins 👇",
   shorts=["One fast food meal and your arteries stiffen for hours. #health #science", "A month of fast food… still there 2.5 years later. #science #nutrition"]),
}
def ts(s): s = int(s); return f"{s // 60}:{s % 60:02d}"
def chapters(film, times):
    start = {t["id"]: t["start"] for t in times}; out, pending = [], None
    for line in open(film, encoding="utf-8"):
        m = re.match(r"#\s*----\s*(.+?)\s*----", line)
        if m: pending = m.group(1).strip(); continue
        k = line.split("|")[0].strip()
        if pending and k in start:
            if pending.upper() not in ("SOURCES", "FACT-CHECK"): out.append((start[k], pending.title().replace("'S", "'s")))
            pending = None
    if out: out[0] = (0, "Hook")
    # YouTube needs chapters >= 10 s apart
    clean = [out[0]]
    for t, n in out[1:]:
        if t - clean[-1][0] >= 10: clean.append((t, n))
    return "\n".join(f"{ts(t)} {n}" for t, n in clean)
def block(film, name):
    rows, on = [], False
    for l in open(film, encoding="utf-8"):
        m = re.match(r"#\s*----\s*(.+?)\s*----", l)
        if m: on = m.group(1).strip().upper() == name; continue
        if on and l.startswith("#"): rows.append(l[1:].strip())
    return rows
def srt(shots, times, out):
    st = {t["id"]: t["start"] for t in times}; ids = [t["id"] for t in times]
    def f(x): h, r = divmod(x, 3600); m, s = divmod(r, 60); return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"
    rows = []
    for sh in shots:
        if sh["id"] not in st: continue
        k = ids.index(sh["id"]); a = st[sh["id"]] + 0.1; b = (st[ids[k + 1]] if k + 1 < len(ids) else a + 8) - 0.45
        words = sh["vo"].split(); chunks, cur = [], []
        for w in words:
            cur.append(w)
            if len(" ".join(cur)) > 38 or w.endswith((".", "?", "!")) and len(cur) > 3: chunks.append(" ".join(cur)); cur = []
        if cur: chunks.append(" ".join(cur))
        tot = sum(len(c) for c in chunks); t = a
        for c in chunks:
            d = (b - a) * len(c) / tot; rows.append(f"{len(rows) + 1}\n{f(t)} --> {f(t + d)}\n{c}\n"); t += d
    open(out, "w", encoding="utf-8").write("\n".join(rows))
def script_md(ep, film, meta, shots):
    m = META[ep]; out = [f"# {ep.upper()} — {m['title']}", "", f"_{CHANNEL} · narration script. Tags like [S3] link each claim to a source below._", ""]
    chap = None; ids = {s["id"]: s for s in shots}
    for l in open(film, encoding="utf-8"):
        mm = re.match(r"#\s*----\s*(.+?)\s*----", l)
        if mm:
            chap = mm.group(1).strip()
            if chap.upper() in ("SOURCES", "FACT-CHECK"): break
            out += ["", f"## {chap.title()}", ""]; continue
        k = l.split("|")[0].strip()
        if k in ids:
            s = ids[k]; cap = f" **[{s['cap']}]**" if s["cap"] else ""
            out.append(f"- `{k}`{cap} {s['raw']}")
    words = sum(len(s["vo"].split()) for s in shots)
    out += ["", f"_Word count: {words} (~{words / 150:.1f} min at 150 wpm)._", "", "## Sources", ""] + [f"- {r}" for r in block(film, "SOURCES")]
    out += ["", "## Fact-check list", ""] + [f"{r}" for r in block(film, "FACT-CHECK")]
    os.makedirs(os.path.join(ROOT, "scripts"), exist_ok=True)
    open(os.path.join(ROOT, "scripts", f"{ep}_script.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
if __name__ == "__main__":
    ep, tj = sys.argv[1], sys.argv[2]; m = META[ep]; film = os.path.join(ROOT, "episodes", ep, ep + ".film")
    meta, sprites, shots = parse(film); times = json.load(open(tj)); n = int(ep[2:])
    def short(r):                                   # "[S1] Who, "Title". URL" — keeps descriptions under 5,000 chars
        urls = re.findall(r"https?://\S+", r); tag = r.split("]", 1)[0] + "]"; body = r.split("]", 1)[1].strip()
        q = re.match(r'^([^"]*"[^"]+")', body)
        if q: body = q.group(1)
        else: body = re.split(r":\s| \(|; | https?://", body)[0].strip().rstrip(".,")
        body = body if len(body) <= 150 else body[:150].rsplit(" ", 1)[0] + "…"
        yr = re.search(r"\b(19|20)\d\d\b", r)
        if "doi.org" in r and yr and yr.group(0) not in body: body += f" ({yr.group(0)})"
        url = next((u.rstrip(";,)") if u.count("(") < u.count(")") else u.rstrip(";,") for u in urls), "")
        return f"{tag} {body}. {url}".strip()
    srcs = "\n".join(short(r) for r in block(film, "SOURCES")).replace("<", "under ").replace(">", "over ")
    desc = f"""{m['hook']}

{m['blurb']}

Every factual claim in this video comes from a source listed below. The jokes are ours. This is entertainment and education, not medical advice.

⏱️ Chapters
{chapters(film, times)}

📚 Sources
{srcs}

🩺 New patient every Wednesday. Subscribe so you don't flatline.

#WhatHappensToYourBody #science #YourVitals"""
    md = f"""# {ep.upper()} upload kit — {CHANNEL}

**Publish:** {m['date']}, 16:00 UTC (11:00 AM New York, 4:00 PM London, 9:00 PM Pakistan). Upload as Private 24 h before, then Schedule.

## Title
{m['title']}

## Thumbnails (YouTube "Test & Compare" with both)
- `thumbs/EP0{n}_A.jpg`
- `thumbs/EP0{n}_B.jpg`

## Description
```
{desc}
```

## Tags
{m['tags']}

## Settings
- Category: **Science & Technology**. Language: English. Captions: upload `episodes/{ep}/{ep}.srt` (English).
- Audience: **No, it's not made for kids**.
- **Altered or synthetic content: Yes.** The narration voice and the pictures are AI-generated. YouTube asks for this label; it does not affect reach.
- Paid promotion: No. Comments: On (hold potentially inappropriate for review).
- End screen (last 20 s): right box = "Best for viewer" video, circle bottom = Subscribe. The left side of the frame is kept clear for the elements.
- Playlist: "What Happens to Your Body If…".
- Video file: render with `python3 pipeline/vfilm.py render episodes/{ep}/{ep}.film out/EP0{n}.mp4` (MP4s are not committed).

## Pinned comment
{m['comment']}

## Shorts (cut from this video, 9:16, 30–50 s, posted Fri and Sun after the long video; link the long video as "Related video")
1. {m['shorts'][0]}
2. {m['shorts'][1]}
"""
    open(os.path.join(ROOT, "episodes", ep, "UPLOAD.md"), "w", encoding="utf-8").write(md)
    srt(shots, times, os.path.join(ROOT, "episodes", ep, ep + ".srt")); script_md(ep, film, meta, shots); print("wrote", ep)
