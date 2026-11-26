"""Write episodes/<ep>/UPLOAD.md: title, description with chapters (from the film's '# ---- NAME ----' markers and the
render's .times.json), tags, pinned comment, schedule. Usage: python3 pipeline/upload_kit.py ep01 path/to/EP01.times.json"""
import json, os, sys, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHANNEL = "Ink and Humanity"
META = {
 "ep01": dict(title="Why It Sucks to Be Born as a Victorian Chimney Sweep", date="Friday 4 December 2026",
   hook="You're 7 years old, stuck inside a chimney, and a law already says you shouldn't be there.",
   blurb="London, 1862. You're born into one damp rented room, sold to a master sweep, and sent up chimneys as narrow as a dinner plate, even though Parliament banned climbing boys years earlier. A mechanical brush could do your job, but you're cheaper.",
   tags="victorian chimney sweep, climbing boys, victorian history, why it sucks to be born as, history animated, victorian london, child labour history, george brewster, percivall pott, dark history, worst jobs in history",
   comment="If you were born in 1862 London, what job do you think you'd get stuck with? 👇 (Wrong answers only.)",
   short="You're 7. You're stuck inside a chimney. And it's already illegal. #history #victorian"),
 "ep02": dict(title="Why It Sucks to Be Born as a Medieval Executioner", date="Friday 11 December 2026",
   hook="Your dad got this job by accident. Now it's yours forever, and nobody will sit next to you in church.",
   blurb="Germany, 1554. A prince needs a hangman, picks your father from the crowd, and your whole family becomes 'dishonourable' overnight. Based on the real diary of Frantz Schmidt, executioner of Nuremberg, who also secretly treated around 15,000 patients.",
   tags="medieval executioner, frantz schmidt, executioner diary, nuremberg, why it sucks to be born as, history animated, dark history, worst jobs in history, early modern germany, hangman",
   comment="Would you take the executioner job if it paid triple? Be honest 👇",
   short="Your dad got this job by accident. Now it's yours. Forever. #history #medieval"),
 "ep03": dict(title="Why It Sucks to Be Born as a Plague Doctor", date="Friday 18 December 2026",
   hook="Bird mask full of flowers, a coat dipped in wax, and every real doctor already ran away.",
   blurb="Venice, 1630. The plague arrives, the famous doctors flee, and the city hires someone young and desperate: you. You get the beak mask, the cane, a big salary and no patients ever again, while the real killer jumps around your ankles.",
   tags="plague doctor, black death, bubonic plague, venice 1630, plague doctor mask, why it sucks to be born as, history animated, dark history, worst jobs in history, quarantine history",
   comment="Be honest: would you have trusted the guy in the bird mask? 👇",
   short="The bird mask was filtering the air. The killer was biting your ankles. #history #plague"),
 "ep04": dict(title="Why It Sucks to Be Born as a Roman Gladiator", date="Friday 25 December 2026",
   hook="50,000 fans, a diet of barley, and a hand signal nobody can explain decides if you live.",
   blurb="Captured on the edge of the Empire, sold to a lanista, fed barley and plant-ash drinks, stitched up by the best doctors in Rome because you're expensive, and then, if you're lucky, set free into a world that has no place for you.",
   tags="roman gladiator, gladiators, ancient rome, colosseum, gladiator diet, why it sucks to be born as, history animated, dark history, ephesus gladiator cemetery, spartacus",
   comment="Which past life should we live next? Most liked comment picks the next episode 👇",
   short="Gladiators were vegetarians. And that's not even the weird part. #history #rome"),
}
def ts(s): s = int(s); return f"{s // 60}:{s % 60:02d}"
def chapters(film, times):
    start = {t["id"]: t["start"] for t in times}; out, pending = [], None
    for line in open(film, encoding="utf-8"):
        m = re.match(r"#\s*----\s*(.+?)\s*----", line)
        if m: pending = m.group(1).split("(")[0].strip().title(); continue
        k = line.split("|")[0].strip()
        if pending and k in start:
            if pending.upper() != "SOURCES": out.append((start[k], pending))
            pending = None
    if out: out[0] = (0, "Hook")
    return "\n".join(f"{ts(t)} {n}" for t, n in out)
def sources(film):
    src = [l[1:].strip() for l in open(film, encoding="utf-8") if re.match(r"#\s*\[S\d+\]", l)]
    if not src:  # EP01 keeps its sources in the long-form script
        md = os.path.join(ROOT, "scripts", "ep01_chimney_sweep.md")
        src = [re.sub(r"\*\*", "", l[2:].strip()) for l in open(md, encoding="utf-8") if l.startswith("- **[S")]
        src.append("[S11] Wikipedia, \"The Water-Babies, A Fairy Tale for a Land Baby\" (Charles Kingsley, 1863). https://en.wikipedia.org/wiki/The_Water-Babies,_A_Fairy_Tale_for_a_Land_Baby")
    return "\n".join(src)
def srt(film, times, out):
    sys.path.insert(0, os.path.join(ROOT, "pipeline")); from film import parse
    _, shots = parse(film); st = {t["id"]: t["start"] for t in times}; ids = [t["id"] for t in times]
    def f(x): h, r = divmod(x, 3600); m, s = divmod(r, 60); return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"
    rows = []
    for k, sh in enumerate(shots):
        if sh["id"] not in st: continue
        a = st[sh["id"]]; b = st[ids[ids.index(sh["id"]) + 1]] - 0.3 if sh["id"] != ids[-1] else a + 8
        words = sh["vo"].split(); chunks = [" ".join(words[i:i + 12]) for i in range(0, len(words), 12)]
        for j, c in enumerate(chunks):
            ca = a + (b - a) * j / len(chunks); cb = a + (b - a) * (j + 1) / len(chunks)
            rows.append(f"{len(rows) + 1}\n{f(ca)} --> {f(cb)}\n{c}\n")
    open(out, "w", encoding="utf-8").write("\n".join(rows))
if __name__ == "__main__":
    ep, tj = sys.argv[1], sys.argv[2]; m = META[ep]; film = os.path.join(ROOT, "episodes", ep, ep + ".film")
    times = json.load(open(tj)); n = int(ep[2:])
    desc = f"""{m['hook']}

{m['blurb']}

Every fact in this video is from a real source (listed below). The jokes are ours.

⏱️ Chapters
{chapters(film, times)}

📚 Sources
{sources(film)}

🔔 A new past life every Friday. Subscribe so you don't miss yours.

#history #WhyItSucks #InkAndHumanity"""
    md = f"""# {ep.upper()} upload kit — {CHANNEL}

**Publish:** {m['date']}, 17:00 UTC (12:00 PM New York, 5:00 PM London, 10:00 PM Pakistan). Upload as Private 24 h before, then Schedule.

## Title
{m['title']}

## Thumbnails (use YouTube "Test & Compare" with both)
- `thumbs/EP0{n}_A.jpg`
- `thumbs/EP0{n}_B.jpg`

## Description
```
{desc}
```

## Tags
{m['tags']}

## Settings
- Category: Education. Language: English. Captions: upload `episodes/{ep}/{ep}.srt`.
- Not made for kids. Altered/synthetic content: **Yes**. The voice and the pictures are AI-generated, and YouTube requires this label for realistic synthetic media. It doesn't affect reach.
- End screen (last 20 s): the right box holds "Best for viewer" plus a Subscribe element.
- Playlist: "Why It Sucks to Be Born as… (Human History)".

## Pinned comment
{m['comment']}

## Short (cut the hook, 0:00 to 0:45, vertical)
{m['short']}
"""
    open(os.path.join(ROOT, "episodes", ep, "UPLOAD.md"), "w", encoding="utf-8").write(md)
    srt(film, times, os.path.join(ROOT, "episodes", ep, ep + ".srt")); print("wrote", ep)
