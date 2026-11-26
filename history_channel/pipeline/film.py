"""Film pipeline: one .film file holds the whole episode (narration + picture + motion), and this script
generates the pictures and renders the finished video with cut-out element animation (no screen shake).

Film file format (one shot per line, '#' starts a comment):
    HERO: text that replaces {hero} in picture descriptions
    id | picture | tokens | caption | narration
picture:  a description (generated to episodes/<ep>/img/<id>.jpg)
          @path        an existing image, relative to history_channel/ (e.g. @scenes/02)
          =id          reuse the picture of an earlier shot (characters stay put, no entrance)
          chimney:@path / chimney:=id   paste the main figure into a code-drawn brick chimney
tokens:   fx: soot birds puffs rain embers sparkle smoke  | camera: zoomin zoomout panl panr hold
          motion of the main figure: struggle bob pulse wag walk static | endcard
Usage:
    python3 pipeline/film.py gen    episodes/ep02/ep02.film [ids...]
    python3 pipeline/film.py render episodes/ep02/ep02.film OUT.mp4 VOICE.onnx [first_n_shots]
"""
import sys, os, math, random, subprocess, wave, tempfile, json, struct
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_test import whiten
from layers import split
from render_v3 import Actor, back_out, smooth, chimney_plate, drop_grey_shadow, Soot, Puffs, Birds

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "..", "style", "fonts", "Kalam-Bold.ttf")
W, H, FPS, S = 1920, 1080, 24, 1080

def parse(path):
    hero, shots = "", []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"): continue
        if line.startswith("HERO:"): hero = line[5:].strip(); continue
        p = [x.strip() for x in line.split("|")]
        if len(p) < 5: continue
        shots.append(dict(id=p[0], pic=p[1], tok=p[2].split(), cap=p[3], vo="|".join(p[4:])))
    return hero, shots

def epdir(path): return os.path.dirname(os.path.abspath(path))

def img_path(film, shots, sh):
    pic = sh["pic"].split(":", 1)[1] if sh["pic"].startswith("chimney:") else sh["pic"]
    if pic.startswith("@"): return os.path.join(ROOT, pic[1:] + ".jpg")
    if pic.startswith("="):
        src = next(s for s in shots if s["id"] == pic[1:]); return img_path(film, shots, src)
    return os.path.join(epdir(film), "img", sh["id"] + ".jpg")

# ---------- generation ----------
def gen(film, ids):
    import gen as G
    hero, shots = parse(film); out = os.path.join(epdir(film), "img"); os.makedirs(out, exist_ok=True)
    todo = [(s["id"], s["pic"].replace("{hero}", hero), out) for s in shots
            if not s["pic"].startswith(("@", "=", "chimney:")) and (not ids or s["id"] in ids)
            and (ids or not os.path.exists(os.path.join(out, s["id"] + ".jpg")))]
    G.HERO = ""                       # the film supplies its own hero text through {hero}
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(6) as ex:
        for r in ex.map(G.run, todo): print(r, flush=True)

# ---------- particles ----------
class Rain:
    def __init__(s, n=70): R = random.Random(3); s.p = [[R.uniform(0, S), R.uniform(0, S), R.uniform(500, 800)] for _ in range(n)]
    def draw(s, cv, t):
        d = ImageDraw.Draw(cv)
        for x, y, v in s.p:
            yy = (y + v * t) % S; d.line([(x, yy), (x - 6, yy + 26)], fill=(90, 110, 140, 200), width=3)
class Embers:
    def __init__(s, n=40): R = random.Random(5); s.p = [[R.uniform(0, S), R.uniform(0, S), R.uniform(40, 90), R.random()] for _ in range(n)]
    def draw(s, cv, t):
        d = ImageDraw.Draw(cv)
        for x, y, v, ph in s.p:
            yy = (y - v * t) % S; xx = x + 20 * math.sin(t * 2 + ph * 6); r = 3 + 2 * math.sin(t * 5 + ph * 9)
            d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(240, 120, 30, 220))
class Sparkle:
    def __init__(s, n=14): R = random.Random(9); s.p = [[R.uniform(150, S - 150), R.uniform(150, S - 250), R.random()] for _ in range(n)]
    def draw(s, cv, t):
        d = ImageDraw.Draw(cv)
        for x, y, ph in s.p:
            k = max(0, math.sin(2 * math.pi * (t * 0.8 + ph))); r = 22 * k
            if r > 1:
                d.line([(x - r, y), (x + r, y)], fill=(240, 190, 30, 255), width=4); d.line([(x, y - r), (x, y + r)], fill=(240, 190, 30, 255), width=4)
class Smoke:
    def __init__(s, n=10): R = random.Random(11); s.p = [[R.uniform(100, S - 100), R.uniform(0, S), R.uniform(25, 50), R.uniform(30, 70)] for _ in range(n)]
    def draw(s, cv, t):
        d = ImageDraw.Draw(cv)
        for x, y, v, r in s.p:
            yy = (y - v * t) % S; rr = r * (1.4 - yy / S)
            d.ellipse([x - rr, yy - rr, x + rr, yy + rr], outline=(120, 120, 120, 120), width=4)
FX = {"soot": lambda: Soot(60, 0, S), "birds": Birds, "rain": Rain, "embers": Embers, "sparkle": Sparkle, "smoke": Smoke}

# ---------- auto choreography ----------
_cache = {}
def cutouts(path):
    if path not in _cache:
        im = whiten(Image.open(path)).resize((S, S), Image.LANCZOS)
        _cache[path] = (im.convert("RGBA"), split(im))
    return _cache[path]

def actors(film, shots, i):
    sh = shots[i]; tok = set(sh["tok"]); path = img_path(film, shots, sh)
    reuse = sh["pic"].removeprefix("chimney:").startswith("=") or "static" in tok
    full, bl = cutouts(path); bl = [b for b in bl if b["area"] > 250]
    base = Image.new("RGBA", (S, S), (255, 255, 255, 255)); lays = []
    if sh["pic"].startswith("chimney:"):
        base = chimney_plate(); main = bl[0]; img = drop_grey_shadow(main["img"])
        lays.append(Soot(45))
        if "puffs" in tok: lays.append(Puffs(540, 760))
        lays.append(Actor(img, 540, 760, scale=min(1.0, 380 / main["w"]), enter="none",
                          idle="struggle" if "struggle" in tok else "breathe"))
        return base, lays
    big = [b for b in bl if b["w"] * b["h"] > 0.42 * S * S]
    small = [b for b in bl if b not in big]
    for b in big: base.alpha_composite(b["img"], (b["x"], b["y"]))       # scenery stays still
    for k, b in enumerate(small):
        cx = (b["x"] + b["w"] / 2) / S; tiny = b["area"] < 0.012 * S * S
        if reuse: enter = "none"
        elif k == 0 and ("walk" in tok): enter = "walk_left" if cx < 0.5 else "walk_right"
        elif k == 0 and not big and cx < 0.3: enter = "walk_left"
        elif k == 0 and not big and cx > 0.7: enter = "walk_right"
        else: enter = "pop"
        idle = "bob" if tiny else "breathe"
        if k == 0:
            for m in ("struggle", "bob", "pulse", "wag"):
                if m in tok: idle = m
        lays.append(Actor.from_blob(b, enter=enter, delay=0 if k == 0 else 0.25 + 0.12 * k, idle=idle))
    lays.reverse()                                     # small things drawn on top of big ones
    for f in FX:
        if f in tok: lays.append(FX[f]())
    if "puffs" in tok and small: lays.append(Puffs(small[0]["x"] + small[0]["w"] / 2, small[0]["y"] + small[0]["h"] * 0.4))
    return base, lays

def camera(tok, i):
    if "hold" in tok: return (1.0, 1.0, 0)
    if "zoomin" in tok: return (1.0, 1.16, 0)
    if "zoomout" in tok: return (1.16, 1.0, 0)
    if "panl" in tok: return (1.12, 1.12, 110)
    if "panr" in tok: return (1.12, 1.12, -110)
    return (1.0, 1.05, 0) if i % 2 == 0 else (1.05, 1.0, 0)

# ---------- render ----------
def render_shot(args):
    film, shots, i, nframes, out = args
    sh = shots[i]; tok = sh["tok"]; base, lays = actors(film, shots, i); cam = camera(tok, i)
    font = ImageFont.truetype(FONT, 72); fbig = ImageFont.truetype(FONT, 96)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    cap = sh["cap"]
    for f in range(nframes):
        t = f / FPS; cv = base.copy()
        for l in lays: l.draw(cv, t)
        e = smooth(f / max(nframes - 1, 1)); z = cam[0] + (cam[1] - cam[0]) * e
        sz = int(S * z); img = cv.convert("RGB").resize((sz, sz), Image.BILINEAR)
        fr = Image.new("RGB", (W, H), "white")
        x0 = (W - sz) // 2 + int(cam[2] * (e - 0.5)) - (300 if "endcard" in tok else 0)
        fr.paste(img, (x0, (H - sz) // 2))
        dr = ImageDraw.Draw(fr)
        if cap:
            k = back_out(f / (0.4 * FPS))
            dr.text((W // 2, 95), cap, font=ImageFont.truetype(FONT, max(8, int(72 * k))), fill="black", anchor="mm", stroke_width=6, stroke_fill="white")
            if f > 0.4 * FPS:
                u = smooth((f - 0.4 * FPS) / (0.4 * FPS)); tw = dr.textlength(cap, font=font)
                dr.line([(W // 2 - tw / 2, 140), (W // 2 - tw / 2 + tw * u, 140)], fill="black", width=5)
        if "endcard" in tok:
            k = back_out((f - 12) / (0.5 * FPS))
            if k > 0.05:
                dr.text((1450, 300), "Your next", font=ImageFont.truetype(FONT, max(8, int(80 * k))), fill="black", anchor="mm")
                dr.text((1450, 400), "past life", font=ImageFont.truetype(FONT, max(8, int(110 * k))), fill=(178, 34, 34), anchor="mm")
                dr.rounded_rectangle([1160, 480, 1740, 806], radius=18, outline="black", width=6)
        ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait(); return out

def tts(voice, text, out):
    subprocess.run([sys.executable, "-m", "piper", "-m", voice, "-f", out, "--length-scale", "1.12", "--sentence-silence", "0.3"],
                   input=text.encode(), check=True, capture_output=True)

def render(film, out, voice, limit=None):
    hero, shots = parse(film)
    if limit: shots = shots[:int(limit)]
    tmp = tempfile.mkdtemp(dir=os.environ.get("TMPDIR")); frames = []; pcm = b""; sr = None
    for i, sh in enumerate(shots):
        p = os.path.join(tmp, f"v{i}.wav"); tts(voice, sh["vo"], p)
        with wave.open(p) as w:
            sr = w.getframerate(); data = w.readframes(w.getnframes())
        n = int(math.ceil((len(data) / 2 / sr + 0.6) * FPS))
        if "endcard" in sh["tok"]: n = max(n, 20 * FPS)               # YouTube end screen needs 5-20 s
        need = int(round(n / FPS * sr)) * 2; data = data[:need] + b"\0" * max(0, need - len(data))
        pcm += data; frames.append(n)
    audio = os.path.join(tmp, "vo.wav")
    with wave.open(audio, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm)
    jobs = [(film, shots, i, frames[i], os.path.join(tmp, f"s{i:03d}.mp4")) for i in range(len(shots))]
    with Pool(int(os.environ.get("JOBS", os.cpu_count()))) as pool:
        for k, r in enumerate(pool.imap(render_shot, jobs)): print(f"shot {k + 1}/{len(jobs)}", flush=True)
    lst = os.path.join(tmp, "list.txt"); open(lst, "w").write("".join(f"file '{j[4]}'\n" for j in jobs))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", audio,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    total = sum(frames) / FPS; print(out, f"{total:.1f}s")
    # shot start times, used for chapter timestamps in the description
    json.dump([{"id": s["id"], "start": round(sum(frames[:k]) / FPS, 2)} for k, s in enumerate(shots)],
              open(os.path.splitext(out)[0] + ".times.json", "w"), indent=0)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "gen": gen(sys.argv[2], sys.argv[3:])
    elif cmd == "render": render(sys.argv[2], sys.argv[3], sys.argv[4], *(sys.argv[5:6]))
