"""The Ward Book film pipeline. One .film file holds the whole episode (narration + picture + motion + sources);
this script generates the woodcut pictures and renders the finished video: cut-out element animation (ink-bleed
entrances, idles), particles, parchment + candle-light finish. No screen shake.

Film file format (one shot per line, '#' starts a comment, '# ---- NAME ----' starts a chapter,
'# [S1] ...' is a source line used by upload_kit.py):
    id | picture | tokens | caption | narration
picture:  a description (generated to episodes/<ep>/img/<id>.jpg)
          =id      reuse the picture of an earlier shot (no entrance; characters stay put)
          -        blank page (for quote / ward / title cards)
tokens:   fx:      snow dust embers fog bats wind rain
          camera:  zoomin zoomout panl panr hold
          motion of the main figure: breathe sway loom creep bob pulse struggle wag shiver static walk
          night    darker candle light            flame   a candle flame under the main figure
          ward     caption 'III|rule text' -> rubric card in the left margin (the ward number then shows top-left
                   until the next chapter)
          quote    caption 'quote text — source' -> a printed quotation page
          title    caption 'Krampus' -> 'How to Survive / Krampus' title plate, art on the left
          endcard  caption = next episode name; art moves left, end-screen box on the right (20 s minimum)
Usage:
    python3 pipeline/film.py gen    episodes/ep01/ep01.film [ids...]
    python3 pipeline/film.py render episodes/ep01/ep01.film OUT.mp4 [first_n_shots]
    python3 pipeline/film.py still  episodes/ep01/ep01.film shot_id OUT.jpg [t]
"""
import sys, os, math, subprocess, wave, tempfile, json, re
from multiprocessing import Pool
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wardlib as L
from wardlib import Actor, smooth, back_out, font, W, H, FPS, S, INK, OCHRE, PAPER
from layers import split

ROOT = L.ROOT
VOICE = os.path.join(ROOT, "voices", "en_GB-alan-medium.onnx")
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]

def parse(path):
    shots, chapter, ward = [], "", None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        m = re.match(r"#\s*----\s*(.+?)\s*----", line)
        if m: chapter = m.group(1); ward = None; continue
        if not line.strip() or line.lstrip().startswith("#"): continue
        p = [x.strip() for x in line.split("|")]
        if len(p) < 5: continue
        tok = p[2].split()
        if "ward" in tok and len(p) >= 6:
            ward = p[3]; sh = dict(id=p[0], pic=p[1], tok=tok, cap=p[3] + "|" + p[4], vo="|".join(p[5:]), chapter=chapter, ward=ward)
        else:
            sh = dict(id=p[0], pic=p[1], tok=tok, cap=p[3], vo="|".join(p[4:]), chapter=chapter, ward=ward)
        shots.append(sh)
    return shots

def epdir(path): return os.path.dirname(os.path.abspath(path))
def img_path(film, shots, sh):
    pic = sh["pic"]
    if pic == "-": return None
    if pic.startswith("="): return img_path(film, shots, next(s for s in shots if s["id"] == pic[1:]))
    return os.path.join(epdir(film), "img", sh["id"] + ".jpg")

# ---------- generation ----------
def gen(film, ids):
    import gen as G
    shots = parse(film); out = os.path.join(epdir(film), "img"); os.makedirs(out, exist_ok=True)
    todo = [(s["id"], s["pic"], out) for s in shots if s["pic"] != "-" and not s["pic"].startswith("=")
            and (not ids or s["id"] in ids) and (ids or not os.path.exists(os.path.join(out, s["id"] + ".jpg")))]
    print(len(todo), "pictures to generate", flush=True)
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(6) as ex:
        for r in ex.map(G.run, todo): print(r, flush=True)

# ---------- choreography ----------
_cache = {}
def cutouts(path):
    if path not in _cache:
        im = L.whiten(Image.open(path)).resize((S, S), Image.LANCZOS)
        _cache[path] = split(im)
    return _cache[path]

def actors(film, shots, i):
    sh = shots[i]; tok = set(sh["tok"]); path = img_path(film, shots, sh)
    base = Image.new("RGBA", (S, S), (255, 255, 255, 255)); lays = []
    if path is None: return base, lays
    reuse = sh["pic"].startswith("=") or "static" in tok
    bl = [b for b in cutouts(path) if b["area"] > 250]
    scenery = [b for b in bl if b["w"] > 0.82 * S and b["h"] > 0.55 * S]     # full-width backdrops stay still
    figs = [b for b in bl if b not in scenery]
    back, front = [], []
    for b in scenery:
        if reuse: base.alpha_composite(b["img"], (b["x"], b["y"]))
        else: back.append(Actor.from_blob(b, enter="ink", idle="none"))
    for k, b in enumerate(figs):
        cx = (b["x"] + b["w"] / 2) / S; tiny = b["area"] < 0.01 * S * S
        if reuse: enter = "none"
        elif k == 0 and "walk" in tok: enter = "walk_left" if cx < 0.5 else "walk_right"
        else: enter = "ink"
        idle = "bob" if tiny else "breathe"
        if k == 0:
            for m in ("sway", "loom", "creep", "bob", "pulse", "struggle", "wag", "shiver"):
                if m in tok: idle = m
        delay = (0.25 if back else 0) + (0 if k == 0 else 0.3 + 0.12 * k)
        front.append(Actor.from_blob(b, enter=enter, delay=delay, idle=idle))
    lays = back + front[::-1]                          # small things drawn on top of big ones
    for f in L.FX:
        if f in tok: lays.append(L.FX[f]())
    if "flame" in tok and figs: lays.append(L.Flame(figs[0]["x"] + figs[0]["w"] / 2, figs[0]["y"] + 40))
    return base, lays

def camera(tok, i):
    if "hold" in tok: return (1.0, 1.0, 0)
    if "zoomin" in tok: return (1.0, 1.14, 0)
    if "zoomout" in tok: return (1.14, 1.0, 0)
    if "panl" in tok: return (1.12, 1.12, 110)
    if "panr" in tok: return (1.12, 1.12, -110)
    return (1.0, 1.05, 0) if i % 2 == 0 else (1.05, 1.0, 0)

# ---------- overlays ----------
def ward_card(dr, num, text, k):
    """Rubric card in the left margin: 'WARD', a big red numeral, the rule in Fell italic."""
    if k <= 0.02: return
    x0, x1, cx = 34, 404, 219; off = int((1 - k) * -40)
    dr.rectangle([x0 + off, 250, x1 + off, 830], outline=INK, width=3)
    dr.rectangle([x0 + 9 + off, 259, x1 - 9 + off, 821], outline=OCHRE, width=2)
    dr.text((cx + off, 315), "WARD", font=font(L.F_SC, 46), fill=INK, anchor="mm")
    dr.text((cx + off, 405), num, font=font(L.F_BLACK, 120), fill=OCHRE, anchor="mm")
    L.ornament(dr, cx + off, 480, 250)
    f = font(L.F_ITAL, 52); lines = L.wrap(dr, text, f, 310)
    y = 520 + max(0, (5 - len(lines))) * 30
    for ln in lines:
        dr.text((cx + off, y), ln, font=f, fill=INK, anchor="ma"); y += 62

def caption(dr, cap, f, nframes):
    k = smooth(f / (0.5 * FPS))
    if k <= 0.02: return
    fnt = font(L.F_SC, 66); tw = dr.textlength(cap, font=fnt)
    dr.text((W // 2, 88), cap, font=fnt, fill=INK, anchor="mm", stroke_width=7, stroke_fill=(255, 255, 255))
    u = smooth((f - 0.3 * FPS) / (0.5 * FPS))
    if u > 0: L.ornament(dr, W // 2, 136, (tw + 60) * u)

def quote_page(dr, text, f):
    k = smooth(f / (0.8 * FPS))
    q, _, src = text.partition("—")
    fnt = font(L.F_ITAL, 62); lines = L.wrap(dr, "“" + q.strip() + "”", fnt, 1150)
    y = H / 2 - len(lines) * 40 - 30
    col = tuple(int(255 - (255 - c) * k) for c in INK)
    for ln in lines: dr.text((W // 2, y), ln, font=fnt, fill=col, anchor="ma"); y += 80
    if src.strip():
        L.ornament(dr, W // 2, y + 30, 360 * k)
        dr.text((W // 2, y + 70), src.strip(), font=font(L.F_SC, 44), fill=tuple(int(255 - (255 - c) * k) for c in OCHRE), anchor="ma")

def title_plate(dr, name, f):
    k = back_out((f - 6) / (0.6 * FPS)); u = smooth((f - 14) / (0.6 * FPS))
    if k > 0.05:
        dr.text((1450, 330), "How to Survive", font=font(L.F_SC, int(70 * min(k, 1.2))), fill=INK, anchor="mm")
    if u > 0.02:
        dr.text((1450, 470), name, font=font(L.F_BLACK, 150), fill=tuple(int(255 - (255 - c) * u) for c in OCHRE), anchor="mm")
        L.ornament(dr, 1450, 575, 460 * u)
        dr.text((1450, 630), "according to folklore", font=font(L.F_ITAL, 46), fill=tuple(int(255 - (255 - c) * u) for c in INK), anchor="mm")

def end_plate(dr, nxt, f):
    k = smooth((f - 12) / (0.6 * FPS))
    if k <= 0.02: return
    col = tuple(int(255 - (255 - c) * k) for c in INK); red = tuple(int(255 - (255 - c) * k) for c in OCHRE)
    dr.text((1450, 250), "Next in the Ward Book", font=font(L.F_SC, 58), fill=col, anchor="mm")
    dr.text((1450, 340), nxt, font=font(L.F_BLACK, 96), fill=red, anchor="mm")
    dr.rectangle([1160, 430, 1740, 756], outline=col, width=4); dr.rectangle([1170, 440, 1730, 746], outline=red, width=2)
    dr.text((1450, 830), "Learn the rules before dark.", font=font(L.F_ITAL, 44), fill=col, anchor="mm")

def frame_at(film, shots, i, f, nframes, base, lays):
    sh = shots[i]; tok = sh["tok"]; cam = camera(tok, i); t = f / FPS
    cv = base.copy()
    for l in lays: l.draw(cv, t)
    e = smooth(f / max(nframes - 1, 1)); z = cam[0] + (cam[1] - cam[0]) * e
    sz = int(S * z); img = cv.convert("RGB").resize((sz, sz), Image.BILINEAR)
    fr = Image.new("RGB", (W, H), "white")
    shift = -300 if ("endcard" in tok or "title" in tok) else 0
    fr.paste(img, ((W - sz) // 2 + int(cam[2] * (e - 0.5)) + shift, (H - sz) // 2))
    dr = ImageDraw.Draw(fr)
    if "ward" in tok:
        num, _, text = sh["cap"].partition("|"); ward_card(dr, num, text, smooth((f - 4) / (0.7 * FPS)))
    elif "quote" in tok: quote_page(dr, sh["cap"], f)
    elif "title" in tok: title_plate(dr, sh["cap"], f)
    elif "endcard" in tok: end_plate(dr, sh["cap"], f)
    elif sh["cap"]: caption(dr, sh["cap"], f, nframes)
    if sh["ward"] and "ward" not in tok and "endcard" not in tok:          # running head: which ward we're on
        dr.text((70, 60), "Ward " + sh["ward"], font=font(L.F_SC, 44), fill=OCHRE, anchor="la")
    return L.finish(fr, t + i * 3.7, dark=0.55 if "night" in tok else 0.0)

def render_shot(args):
    film, shots, i, nframes, out = args
    base, lays = actors(film, shots, i)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for f in range(nframes): ff.stdin.write(frame_at(film, shots, i, f, nframes, base, lays).tobytes())
    ff.stdin.close(); ff.wait(); return out

def tts(text, out):
    subprocess.run([sys.executable, "-m", "piper", "-m", VOICE, "-f", out, "--length-scale", "1.1", "--sentence-silence", "0.35"],
                   input=text.encode(), check=True, capture_output=True)

def render(film, out, limit=None):
    shots = parse(film)
    if limit: shots = shots[:int(limit)]
    tmp = tempfile.mkdtemp(dir=os.environ.get("TMPDIR")); frames = []; pcm = b""; sr = None
    texts = [sh["vo"] for sh in shots]
    def one(k):
        p = os.path.join(tmp, f"v{k}.wav")
        if texts[k].strip(): tts(texts[k], p)
        return p
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(4) as ex: wavs = list(ex.map(one, range(len(shots))))
    for i, sh in enumerate(shots):
        if os.path.exists(wavs[i]):
            with wave.open(wavs[i]) as w: sr = w.getframerate(); data = w.readframes(w.getnframes())
        else: data = b""
        sr = sr or 22050
        pad = 1.4 if ("quote" in sh["tok"] or "title" in sh["tok"] or "ward" in sh["tok"]) else 0.6
        n = int(math.ceil((len(data) / 2 / sr + pad) * FPS))
        if "endcard" in sh["tok"]: n = max(n, 20 * FPS)
        need = int(round(n / FPS * sr)) * 2; data = data[:need] + b"\0" * max(0, need - len(data))
        pcm += data; frames.append(n)
    vo = os.path.join(tmp, "vo.wav")
    with wave.open(vo, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm)
    total = sum(frames) / FPS
    # voice with a small stone-room echo, over a low wind drone; loudness to about -14 LUFS
    audio = os.path.join(tmp, "mix.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vo,
                    "-f", "lavfi", "-t", f"{total:.2f}", "-i", "anoisesrc=color=brown:amplitude=0.5:seed=3",
                    "-filter_complex",
                    "[0:a]aresample=44100,aecho=0.8:0.6:60|120:0.18|0.10,highpass=f=70[v];"
                    "[1:a]aresample=44100,lowpass=f=320,volume=0.06,tremolo=f=0.1:d=0.5[d];"
                    "[v][d]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11",
                    "-ar", "44100", "-ac", "2", audio], check=True)
    jobs = [(film, shots, i, frames[i], os.path.join(tmp, f"s{i:03d}.mp4")) for i in range(len(shots))]
    with Pool(int(os.environ.get("JOBS", os.cpu_count()))) as pool:
        for k, r in enumerate(pool.imap_unordered(render_shot, jobs)): print(f"shot {k + 1}/{len(jobs)}", flush=True)
    lst = os.path.join(tmp, "list.txt"); open(lst, "w").write("".join(f"file '{j[4]}'\n" for j in jobs))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", audio,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
    print(out, f"{total:.1f}s")
    json.dump([{"id": s["id"], "start": round(sum(frames[:k]) / FPS, 2)} for k, s in enumerate(shots)] + [{"id": "_end", "start": round(total, 2)}],
              open(os.path.splitext(out)[0] + ".times.json", "w"), indent=0)

def still(film, sid, out, t=2.0):
    shots = parse(film); i = next(k for k, s in enumerate(shots) if s["id"] == sid)
    base, lays = actors(film, shots, i); n = int(8 * FPS)
    frame_at(film, shots, i, int(float(t) * FPS), n, base, lays).save(out, quality=90)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "gen": gen(sys.argv[2], sys.argv[3:])
    elif cmd == "render": render(sys.argv[2], sys.argv[3], *(sys.argv[4:5]))
    elif cmd == "still": still(*sys.argv[2:])
