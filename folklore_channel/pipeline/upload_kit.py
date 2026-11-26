"""Write episodes/<ep>/UPLOAD.md (title, description with chapters + sources, tags, pinned comment, schedule) and
episodes/<ep>/<ep>.srt from the film and the render's .times.json.
Also writes scripts/<ep>_script.md (the narration as a readable script, with sources and the fact-check list).
Usage: python3 pipeline/upload_kit.py ep01 renders/EP01.times.json"""
import json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from film import parse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHANNEL = "The Ward Book"
META = {
 "ep01": dict(title="How to Survive Krampus (According to Folklore)", date="Wednesday 2 December 2026", short_date="Saturday 5 December 2026 (Krampusnacht)",
   hook="It's the 5th of December in the Alps. You hear bells, and a chain dragging on stone. Here are the five rules that get you to morning.",
   blurb="Krampus, the horned servant of Saint Nicholas, walks the Alpine villages on Krampusnacht with birch rods, chains and a basket for naughty children. We open the Ward Book on the five folk rules for surviving him, where he really comes from (a pagan spirit or a stage devil?), and the one thing that ever managed to scare him off: a 1930s government.",
   tags="krampus, krampusnacht, krampus legend, krampus origin, how to survive krampus, saint nicholas, alpine folklore, austrian christmas traditions, krampuslauf, christmas demon, folklore explained, dark folklore, the ward book, christmas folklore",
   comment="Would you survive Krampusnacht? Which ward do you think you'd break first? 👇 (Honesty earns you a golden rod.)",
   short="December 5th. Bells in the street. Here's rule #1 for surviving Krampus. #krampus #folklore #christmas"),
 "ep02": dict(title="How to Survive the Wendigo (According to Folklore)", date="Wednesday 9 December 2026", short_date="Saturday 12 December 2026",
   hook="It's February in the northern forest and the food ran out eleven days ago. This is the one monster you can turn into.",
   blurb="The windigo (wendigo, witiko) comes from Algonquian-speaking peoples of the northern forests: Anishinaabe, Cree, Innu and their neighbours. Drawing on Anishinaabe writer Basil Johnston and on ethnohistorians, we go through five wards from the teaching, the real cases of Swift Runner (1879) and Jack Fiddler (1907), the debate over 'wendigo psychosis', and why the famous antlers aren't in the old accounts.",
   tags="wendigo, windigo, wendigo legend, wendigo origin, how to survive the wendigo, algonquian folklore, ojibwe, cree, anishinaabe, basil johnston, swift runner, jack fiddler, wendigo psychosis, dark folklore, the ward book",
   comment="The Wendigo's wards are about sharing, not salt and iron. Which other legend is secretly a lesson about greed? 👇",
   short="This is the only monster you can turn into. #wendigo #folklore"),
 "ep03": dict(title="How to Survive Baba Yaga (According to Folklore)", date="Wednesday 16 December 2026", short_date="Saturday 19 December 2026",
   hook="A hut on chicken legs, a fence of skulls, and a witch who might help you or eat you. It all depends on her rules.",
   blurb="Baba Yaga flies in a mortar, steers with a pestle and lives in a hut on chicken legs. Straight from Afanasyev's Russian folk tales (Vasilisa the Beautiful, The Frog Princess, Baba Yaga), we open five wards: the words that turn the hut, why you should make her be your host, why you feed her cat, the doll in your pocket, and the question you must never ask. Plus where she really comes from, with Propp, Lomonosov and Bilibin.",
   tags="baba yaga, baba yaga legend, baba yaga origin, how to survive baba yaga, vasilisa the beautiful, slavic folklore, russian fairy tales, hut on chicken legs, afanasyev, vladimir propp, dark folklore, the ward book, slavic mythology",
   comment="Baba Yaga lets you ask about the riders, but never the hands. What question would YOU be dying to ask? 👇",
   short="Before you knock on Baba Yaga's hut, feed the cat. #babayaga #folklore #slavic"),
 "ep04": dict(title="How to Survive the Wild Hunt (According to Folklore)", date="Wednesday 23 December 2026", short_date="Saturday 26 December 2026 (first of the Twelve Nights week)",
   hook="Hounds baying in the sky, riders crossing the clouds, and you on the road alone. Europe agreed on what to do next.",
   blurb="From Norway to the Alps to the English fens, people told of a ghostly hunt that rides the winter sky, led by Wodan, King Herla, Herne, or a cursed lord who hunts forever. Using the legends Jacob Grimm and other collectors wrote down, the 1127 Peterborough Chronicle and Orderic Vitalis's priest Walchelin, we open five wards for the Twelve Nights, and find out how the leader of the dead turned into a clown.",
   tags="wild hunt, the wild hunt legend, wild hunt mythology, how to survive the wild hunt, odin, wodan, rauhnachte, twelve nights, jacob grimm, peterborough chronicle, herne the hunter, harlequin hellequin, germanic folklore, dark folklore, the ward book",
   comment="That's the first chapter of the Ward Book: 4 legends, 20 wards. Which legend should we open next? The most-liked answer becomes the next episode 👇",
   short="If you hear hounds in the sky: face down, eyes shut. #wildhunt #folklore #yule"),
}
def ts(s): s = int(s); return f"{s // 60}:{s % 60:02d}"
def chapters(film, times):
    start = {t["id"]: t["start"] for t in times}; out, pending = [], None
    for line in open(film, encoding="utf-8"):
        m = re.match(r"#\s*----\s*(.+?)\s*----", line)
        if m: pending = m.group(1).strip().title().replace("Ward Iv", "Ward IV").replace("Ward Iii", "Ward III").replace("Ward Ii", "Ward II"); continue
        k = line.split("|")[0].strip()
        if pending and k in start: out.append((start[k], pending)); pending = None
    if out: out[0] = (0, "Hook")
    return "\n".join(f"{ts(t)} {n}" for t, n in out)
def sources(film): return [l.lstrip("#").strip() for l in open(film, encoding="utf-8") if re.match(r"#\s*\[S\d+\]", l)]
def srt(film, times, out):
    shots = parse(film); st = {t["id"]: t["start"] for t in times}; ids = [t["id"] for t in times]
    def f(x): h, r = divmod(x, 3600); m, s = divmod(r, 60); return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"
    rows = []
    for sh in shots:
        if sh["id"] not in st or not sh["vo"].strip(): continue
        a = st[sh["id"]]; b = st[ids[ids.index(sh["id"]) + 1]] - 0.4
        # split at sentence ends first, then into chunks of at most ~10 words, timed by word count
        words = sh["vo"].split(); chunks, cur = [], []
        for w in words:
            cur.append(w)
            if len(cur) >= 10 or (w[-1] in ".?!" and len(cur) >= 4): chunks.append(cur); cur = []
        if cur: chunks.append(cur)
        n = sum(len(c) for c in chunks); t = a
        for c in chunks:
            d = (b - a) * len(c) / n; rows.append(f"{len(rows) + 1}\n{f(t)} --> {f(t + d)}\n{' '.join(c)}\n"); t += d
    open(out, "w", encoding="utf-8").write("\n".join(rows))
def script_md(ep, film, m):
    shots = parse(film); out = [f"# {ep.upper()} — {m['title']}\n", "Narration as recorded (generated from the film file). Ward cards in **bold**.\n"]
    chap = None
    for sh in shots:
        if sh["chapter"] != chap: chap = sh["chapter"]; out.append(f"\n## {chap.title()}\n")
        if "ward" in sh["tok"]: num, _, rule = sh["cap"].partition("|"); out.append(f"**WARD {num}: {rule}**\n")
        if "quote" in sh["tok"]: out.append(f"> *{sh['cap']}*\n")
        if sh["vo"].strip(): out.append(sh["vo"] + "\n")
    out.append("\n## Sources\n"); out += [f"- {s}" for s in sources(film)]
    fc = os.path.join(ROOT, "scripts", f"{ep}_factcheck.md")
    if os.path.exists(fc): out.append("\n" + open(fc, encoding="utf-8").read())
    open(os.path.join(ROOT, "scripts", f"{ep}_script.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
if __name__ == "__main__":
    ep, tj = sys.argv[1], sys.argv[2]; m = META[ep]; film = os.path.join(ROOT, "episodes", ep, ep + ".film")
    times = json.load(open(tj)); n = int(ep[2:]); src = "\n".join(sources(film))
    desc = f"""{m['hook']}

{m['blurb']}

Every factual claim is sourced below. Folklore varies from village to village; where tellings disagree, we say so.

⏱️ Chapters
{chapters(film, times)}

📚 Sources
{src}

🕯️ A new ward every Wednesday. Subscribe so the Ward Book is open when the next legend comes.

Narration voice and illustrations are AI-generated; research and script are human-checked.

#folklore #mythology #TheWardBook"""
    md = f"""# {ep.upper()} upload kit — {CHANNEL}

**Publish:** {m['date']}, 21:00 UTC (4:00 PM New York, 9:00 PM London, 2:00 AM Thursday Pakistan). Upload as Private at least 24 h before, then Schedule.
**Video file:** `renders/EP0{n}.mp4` (rendered locally, not in git; re-render with `python3 pipeline/film.py render episodes/{ep}/{ep}.film renders/EP0{n}.mp4`).

## Title
{m['title']}

## Thumbnails (YouTube "Test & Compare", both)
- `thumbs/EP0{n}_A.jpg`
- `thumbs/EP0{n}_B.jpg`

## Description
```
{desc}
```

## Tags
{m['tags']}

## Settings
- Category: **Education**. Language: English. Captions: upload `episodes/{ep}/{ep}.srt` (English).
- Audience: **No, not made for kids** (dark folklore themes).
- **Altered or synthetic content: Yes.** The narration voice and the pictures are AI-generated.
- Playlist: "How to Survive… (The Ward Book)".
- End screen (last 20 s): video element in the framed box on the right ("Best for viewer" or the next episode), plus a Subscribe element under the title.
- Cards: at the first Ward card, add a card to the previous episode (from EP02 on).

## Pinned comment
{m['comment']}

## Short (cut the hook, first ~45 s, crop to 9:16 around the centre picture)
Post: {m['short_date']}, 17:00 UTC. Set the long video as the Short's "Related video".
Caption: {m['short']}
"""
    open(os.path.join(ROOT, "episodes", ep, "UPLOAD.md"), "w", encoding="utf-8").write(md)
    srt(film, times, os.path.join(ROOT, "episodes", ep, ep + ".srt")); script_md(ep, film, m); print("wrote", ep)
