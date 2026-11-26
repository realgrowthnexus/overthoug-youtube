"""Your Vitals film pipeline: one .film file holds the whole episode (narration + pictures + motion + vitals HUD).
It generates the pictures, then renders the finished video with element animation (no screen shake):
neon sprites that power on, walk, breathe and float; pulsing danger glows; particles; a live vitals monitor.

Film file format ('#' starts a comment, '# ---- NAME ----' starts a chapter):
    METER: label for the top-right meter (e.g. TIME AWAKE, DEPTH)
    SPRITE id | description            a figure/prop generated alone on black, placed with spr: tokens
    id | picture | tokens | caption | narration
picture:  a description (generated to episodes/<ep>/img/<id>.jpg), =id (reuse an earlier picture),
          or - (no picture: empty dark stage, use sprites)
tokens:   camera: zoomin zoomout panl panr hold
          fx: bubbles snow sparks flash zzz rain dust alert beat
          glow (pulse the orange/red danger spots)   split (cut out small elements and animate them)
          spr:ID@x,y,scale[,enter[,idle]]  x,y = feet position in the 1080 stage, enter: on pop walkl walkr drop rise
                                            idle: breathe bob float shake sway
          vitals (persist until changed): hr=72 temp=36.8 t=HOUR_17 s=OK|WARN|CRIT o2=98
          endcard
Usage:
    python3 pipeline/vfilm.py gen    episodes/ep01/ep01.film [ids...]
    python3 pipeline/vfilm.py render episodes/ep01/ep01.film OUT.mp4 [first_n_shots]
"""
import sys, os, math, random, subprocess, wave, tempfile, json, re
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from layers import split

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "fonts")
F_HEAD = os.path.join(FONTS, "Oswald[wght].ttf")
F_MONO = os.path.join(FONTS, "JetBrainsMono[wght].ttf")
F_BIG = os.path.join(FONTS, "Anton-Regular.ttf")
VOICE = os.path.join(ROOT, "voices", "en_GB-cori-high.onnx")
W, H, FPS, S = 1920, 1080, 24, 1080
X0 = (W - S) // 2
BG = (4, 6, 11)
CYAN, AMBER, RED, GREEN, WHITE, DIM = (70, 225, 255), (255, 176, 32), (255, 59, 59), (56, 242, 155), (235, 248, 255), (40, 70, 90)
STATUS = {"OK": GREEN, "WARN": AMBER, "CRIT": RED, "DEAD": (120, 120, 120)}

def font(path, size, wght=None):
    f = ImageFont.truetype(path, size)
    if wght:
        try: f.set_variation_by_axes([wght])
        except Exception: pass
    return f

# ---------------- parsing ----------------
def parse(path):
    meta, sprites, shots = {"METER": "ELAPSED"}, {}, []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"): continue
        m = re.match(r"^([A-Z]+):\s*(.*)$", line)
        if m and "|" not in line: meta[m.group(1)] = m.group(2).strip(); continue
        if line.startswith("SPRITE "):
            k, v = line[7:].split("|", 1); sprites[k.strip()] = v.strip(); continue
        p = [x.strip() for x in line.split("|")]
        if len(p) < 5: continue
        raw = "|".join(p[4:]); shots.append(dict(id=p[0], pic=p[1], tok=p[2].split(), cap=p[3], raw=raw, vo=re.sub(r"\s*\[S[\d, S]+\]", "", raw).strip()))
    # vitals carry forward from shot to shot
    v = dict(hr="72", temp="36.8", t="0", s="OK", o2="98")
    for sh in shots:
        prev = dict(v)
        for t in sh["tok"]:
            if "=" in t and ":" not in t:
                k, val = t.split("=", 1)
                if k in v: v[k] = val
        sh["vit"], sh["vit0"] = dict(v), prev
    return meta, sprites, shots

def epdir(film): return os.path.dirname(os.path.abspath(film))
def img_path(film, shots, sh):
    pic = sh["pic"]
    if pic.startswith("="):
        return img_path(film, shots, next(s for s in shots if s["id"] == pic[1:]))
    if pic == "-": return None
    return os.path.join(epdir(film), "img", sh["id"] + ".jpg")

# ---------------- generation ----------------
def gen(film, ids):
    import gen as G
    meta, sprites, shots = parse(film); out = os.path.join(epdir(film), "img"); os.makedirs(out, exist_ok=True)
    jobs = [(s["id"], s["pic"], out) for s in shots if s["pic"] not in ("-",) and not s["pic"].startswith("=")]
    jobs += [("spr_" + k, G.SPRITE + d, out) for k, d in sprites.items()]
    todo = [j for j in jobs if (ids and (j[0] in ids or j[0].removeprefix("spr_") in ids)) or
            (not ids and not os.path.exists(os.path.join(out, j[0] + ".jpg")))]
    print(len(todo), "pictures to generate", flush=True)
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(6) as ex:
        for r in ex.map(G.run, todo): print(r, flush=True)

# ---------------- easing ----------------
def back_out(t, s=1.7):
    t = min(max(t, 0), 1) - 1; return t * t * ((s + 1) * t + s) + 1
def smooth(t): t = min(max(t, 0), 1); return t * t * (3 - 2 * t)

# ---------------- screen blending (neon on black composites perfectly) ----------------
def screen(base, layer, x, y, alpha=1.0):
    """base: float32 HxWx3 in 0..1 (modified in place). layer: float32 hxwx3."""
    h, w = layer.shape[:2]; x, y = int(x), int(y)
    bx0, by0 = max(x, 0), max(y, 0); bx1, by1 = min(x + w, base.shape[1]), min(y + h, base.shape[0])
    if bx1 <= bx0 or by1 <= by0: return
    L = layer[by0 - y:by1 - y, bx0 - x:bx1 - x] * alpha
    B = base[by0:by1, bx0:bx1]
    base[by0:by1, bx0:bx1] = 1 - (1 - B) * (1 - L)

def to_f(im): return np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0
def darken_bg(im):
    """Push the near-black backdrop of a generated picture to true black so it blends into the frame."""
    a = to_f(im); lum = a.max(2, keepdims=True)
    k = np.clip((lum - 0.06) / 0.10, 0, 1)
    return a * k

# ---------------- sprites ----------------
class Sprite:
    def __init__(s, arr, x, y, scale, enter="on", idle="breathe", delay=0.0, ph=0.0):
        s.src, s.x, s.y, s.scale, s.enter, s.idle, s.delay, s.ph = arr, x, y, scale, enter, idle, delay, ph
        s.cache = {}
    def frame(s, sx, sy, ang):
        key = (round(sx, 3), round(sy, 3), round(ang, 1))
        if key not in s.cache:
            h, w = s.src.shape[:2]
            im = Image.fromarray((s.src * 255).astype(np.uint8)).resize((max(1, int(w * sx)), max(1, int(h * sy))), Image.BILINEAR)
            if abs(ang) > 0.05: im = im.rotate(ang, resample=Image.BILINEAR, expand=True)
            if len(s.cache) > 400: s.cache.clear()
            s.cache[key] = np.asarray(im, dtype=np.float32) / 255.0
        return s.cache[key]
    def draw(s, cv, t):
        lt = t - s.delay; a = 1.0
        if lt < 0: return
        sx = sy = s.scale; ang = dx = dy = 0.0
        if s.enter == "on":                                   # neon power-on flicker
            a = 0.0 if lt < 0.05 else (0.3 if lt < 0.12 else (0.05 if lt < 0.18 else min(1, 0.4 + lt * 2)))
        elif s.enter == "pop":
            k = max(back_out(lt / 0.45), 0.02); sx *= k; sy *= k
        elif s.enter in ("walkl", "walkr"):
            k = smooth(lt / 1.4); dx = (1 - k) * 640 * (-1 if s.enter == "walkl" else 1)
            if k < 1: dy -= abs(math.sin(lt * 9)) * 14; ang += 3 * math.sin(lt * 9)
        elif s.enter == "drop":
            k = back_out(lt / 0.6, 1.2); dy -= (1 - k) * 700
        elif s.enter == "rise":
            k = smooth(lt / 1.0); dy += (1 - k) * 300; a = k
        p = 2 * math.pi
        if s.idle == "breathe":
            b = math.sin(p * (t / 2.6 + s.ph)); sy *= 1 + 0.018 * b; sx *= 1 - 0.006 * b; ang += 0.8 * math.sin(p * (t / 3.9 + s.ph))
        elif s.idle == "bob":
            dy += 9 * math.sin(p * (t / 1.5 + s.ph)); ang += 3 * math.sin(p * (t / 2.2 + s.ph))
        elif s.idle == "float":
            dy += 18 * math.sin(p * (t / 4.0 + s.ph)); ang += 4 * math.sin(p * (t / 5.3 + s.ph)); dx += 10 * math.sin(p * (t / 6.1))
        elif s.idle == "shake":                               # the element trembles, not the camera
            dx += 4 * math.sin(t * 61); ang += 1.2 * math.sin(t * 47)
        elif s.idle == "sway":
            ang += 5 * math.sin(p * (t / 1.6 + s.ph))
        im = s.frame(sx, sy, ang)
        h, w = im.shape[:2]
        screen(cv, im, s.x - w / 2 + dx, s.y - h + dy, a)

_spr = {}
def sprite_arr(path):
    if path not in _spr:
        im = Image.open(path).convert("RGB")
        arr = darken_bg(im)
        ys, xs = np.where(arr.max(2) > 0.02)
        if len(xs): arr = arr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        _spr[path] = arr
    return _spr[path]

# ---------------- particles ----------------
class Bubbles:
    def __init__(s, n=34): R = random.Random(3); s.p = [[R.uniform(80, S - 80), R.uniform(0, S), R.uniform(50, 120), R.uniform(4, 14), R.random()] for _ in range(n)]
    def draw(s, d, t):
        for x, y, v, r, ph in s.p:
            yy = (y - v * t) % S; xx = x + 12 * math.sin(t * 2 + ph * 6)
            d.ellipse([xx - r, yy - r, xx + r, yy + r], outline=CYAN + (170,), width=2)
class Snow:   # marine snow drifting down
    def __init__(s, n=90): R = random.Random(4); s.p = [[R.uniform(0, S), R.uniform(0, S), R.uniform(10, 35), R.uniform(1.5, 3.5)] for _ in range(n)]
    def draw(s, d, t):
        for x, y, v, r in s.p:
            yy = (y + v * t) % S; xx = x + 8 * math.sin(t * 0.7 + y)
            d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(170, 220, 235, 140))
class Dust:
    def __init__(s, n=40): R = random.Random(5); s.p = [[R.uniform(0, S), R.uniform(0, S), R.uniform(-10, 10), R.uniform(-8, 8), R.random()] for _ in range(n)]
    def draw(s, d, t):
        for x, y, vx, vy, ph in s.p:
            xx, yy = (x + vx * t) % S, (y + vy * t) % S; k = 0.5 + 0.5 * math.sin(t * 2 + ph * 9)
            d.ellipse([xx - 2, yy - 2, xx + 2, yy + 2], fill=CYAN + (int(60 + 120 * k),))
class Rain:
    def __init__(s, n=70): R = random.Random(6); s.p = [[R.uniform(0, S), R.uniform(0, S), R.uniform(700, 1000)] for _ in range(n)]
    def draw(s, d, t):
        for x, y, v in s.p:
            yy = (y + v * t) % S; d.line([(x, yy), (x - 5, yy + 30)], fill=(90, 160, 210, 150), width=2)
class Sparks:
    def __init__(s): s.R = random.Random(7)
    def draw(s, d, t):
        R = random.Random(int(t * 12))
        for _ in range(3):
            x, y = R.uniform(200, S - 200), R.uniform(150, S - 300); pts = [(x, y)]
            for _ in range(5): x += R.uniform(-40, 40); y += R.uniform(10, 45); pts.append((x, y))
            d.line(pts, fill=(255, 245, 160, 230), width=3)
class Zzz:
    def __init__(s): s.f = font(F_BIG, 60)
    def draw(s, d, t):
        for k in range(3):
            c = (t * 0.5 + k / 3) % 1; x = 820 + 90 * c + 20 * math.sin(c * 6); y = 380 - 260 * c
            d.text((x, y), "Z", font=s.f, fill=CYAN + (int(255 * (1 - c)),), anchor="mm")
FX = {"bubbles": Bubbles, "snow": Snow, "dust": Dust, "rain": Rain, "sparks": Sparks, "zzz": Zzz}

# ---------------- HUD ----------------
class HUD:
    def __init__(s, meta):
        s.meta = meta
        s.f_lab = font(F_MONO, 22, 500); s.f_num = font(F_BIG, 96); s.f_mid = font(F_BIG, 54)
        s.f_brand = font(F_HEAD, 30, 600); s.f_cap = font(F_HEAD, 58, 600); s.f_small = font(F_MONO, 20, 400)
        s.plate = s.make_plate()
    def make_plate(s):
        im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
        for x in range(0, W, 60): d.line([(x, 0), (x, H)], fill=(9, 14, 22))
        for y in range(0, H, 60): d.line([(0, y), (W, y)], fill=(9, 14, 22))
        for x0 in (28, W - 392):                                   # side panels
            d.rounded_rectangle([x0, 40, x0 + 364, H - 40], radius=18, outline=(22, 52, 66), width=2, fill=(5, 9, 15))
        d.text((210, 78), "YOUR VITALS", font=s.f_brand, fill=CYAN, anchor="mm")
        for y, lab in ((150, "HEART RATE  bpm"), (450, "CORE TEMP  °C"), (680, "BLOOD OXYGEN  %")):
            d.text((52, y), lab, font=s.f_lab, fill=(90, 150, 170))
        d.text((W - 368, 78), s.meta.get("METER", "ELAPSED"), font=s.f_lab, fill=(90, 150, 170))
        d.text((W - 368, 300), "STATUS", font=s.f_lab, fill=(90, 150, 170))
        d.text((W - 368, 470), "PATIENT", font=s.f_lab, fill=(90, 150, 170))
        d.text((W - 368, 500), "YOU", font=s.f_mid, fill=WHITE)
        d.text((W - 368, 570), s.meta.get("CASE", ""), font=s.f_small, fill=(90, 150, 170))
        return np.asarray(im, dtype=np.float32) / 255.0
    @staticmethod
    def lerp(a, b, k):
        try:
            fa, fb = float(a), float(b); v = fa + (fb - fa) * k
            return f"{v:.1f}" if ("." in a or "." in b) else f"{int(round(v))}"
        except ValueError: return b
    def draw(s, d, t, sh, cv_ecg=None):
        v0, v = sh["vit0"], sh["vit"]; k = smooth(t / 1.0)
        hr = s.lerp(v0["hr"], v["hr"], k); temp = s.lerp(v0["temp"], v["temp"], k); o2 = s.lerp(v0["o2"], v["o2"], k)
        st = v["s"]; col = STATUS.get(st, AMBER)
        blink = st == "CRIT" and int(t * 3) % 2 == 0
        d.text((52, 180), hr, font=s.f_num, fill=RED if st == "CRIT" else col)
        d.text((52, 478), temp, font=s.f_num, fill=WHITE)
        d.text((52, 708), o2, font=s.f_num, fill=WHITE)
        # ECG trace scrolling at the heart rate
        try: bpm = max(0.0, float(hr))
        except ValueError: bpm = 72
        x0, y0, wd = 52, 370, 316; pts = []
        for i in range(wd):
            if bpm < 1: y = 0
            else:
                ph = ((i / wd) * 3.2 * bpm / 72 - t * bpm / 60) % 1
                y = (-60 if 0.10 < ph < 0.13 else 25 if 0.13 < ph < 0.16 else -8 if 0.30 < ph < 0.38 else 0)
            pts.append((x0 + i, y0 + y))
        d.line(pts, fill=(col if st != "CRIT" else RED) + (255,), width=3)
        # meter + status
        d.text((W - 368, 110), v["t"].replace("_", " "), font=s.f_num if len(v["t"]) < 9 else s.f_mid, fill=WHITE)
        if not blink: d.text((W - 368, 330), st if st != "DEAD" else "FLATLINE", font=s.f_num, fill=col)
        # pulsing heart dot
        if bpm > 1:
            c = (t * bpm / 60) % 1; r = 10 + 8 * max(0, 1 - c * 4)
            d.ellipse([330 - r, 120 + 46 - r, 330 + r, 120 + 46 + r], fill=RED)
        # recording dot + small footer
        d.text((W - 368, H - 92), "● REC   SIMULATION", font=s.f_small, fill=RED if int(t * 2) % 2 else (120, 30, 30))
        d.text((52, H - 92), "Sources in description", font=s.f_small, fill=(70, 110, 130))

# ---------------- shot assembly ----------------
_cut = {}
def scene(film, shots, sh):
    p = img_path(film, shots, sh)
    if p is None: return np.zeros((S, S, 3), np.float32), None, []
    if p not in _cut:
        im = Image.open(p).convert("RGB").resize((S, S), Image.LANCZOS)
        arr = darken_bg(im)
        a8 = (arr * 255).astype(np.uint8)
        r, g, b = [a8[..., i].astype(int) for i in range(3)]
        hot = ((r > 150) & (r > g + 40) & (r > b + 60)).astype(np.float32)
        hot = np.asarray(Image.fromarray((hot * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)), np.float32)[..., None] / 255.0
        _cut[p] = (arr, hot, im)
    arr, hot, im = _cut[p]
    blobs = []
    if "split" in sh["tok"]:
        els, _ = split(im)
        big = [e for e in els if e["w"] * e["h"] > 0.35 * S * S]
        if big or len(els) > 1:
            base = np.zeros_like(arr)
            small = [e for e in els if e not in big]
            mask = np.zeros((S, S), np.float32)
            for e in big:
                al = np.asarray(e["img"].getchannel("A"), np.float32) / 255.0
                mask[e["y"]:e["y"] + e["h"], e["x"]:e["x"] + e["w"]] = np.maximum(mask[e["y"]:e["y"] + e["h"], e["x"]:e["x"] + e["w"]], al)
            base = arr * mask[..., None]
            for k, e in enumerate(small):
                a = np.asarray(e["img"], np.float32) / 255.0; spr = a[..., :3] * a[..., 3:4]
                blobs.append(Sprite(spr, e["x"] + e["w"] / 2, e["y"] + e["h"], 1.0, enter="pop", idle="bob" if e["area"] < 0.01 * S * S else "breathe",
                                    delay=0.15 * k, ph=k * 0.37))
            return base, hot * (mask[..., None] > 0), blobs
    return arr, hot, blobs

def sprites_for(film, sh):
    out = []
    for k, t in enumerate(sh["tok"]):
        if not t.startswith("spr:"): continue
        name, rest = t[4:].split("@", 1); parts = rest.split(",")
        x, y, sc = float(parts[0]), float(parts[1]), float(parts[2])
        enter = parts[3] if len(parts) > 3 else ("none" if "=" in sh["pic"] else "on")
        idle = parts[4] if len(parts) > 4 else "breathe"
        arr = sprite_arr(os.path.join(epdir(film), "img", "spr_" + name + ".jpg"))
        out.append(Sprite(arr, x, y, sc * 900 / max(arr.shape[:2]), enter=enter, idle=idle, delay=0.1 * k, ph=k * 0.29))
    return out

def camera(tok, i):
    if "hold" in tok: return (1.0, 1.0, 0)
    if "zoomin" in tok: return (1.0, 1.14, 0)
    if "zoomout" in tok: return (1.14, 1.0, 0)
    if "panl" in tok: return (1.12, 1.12, 100)
    if "panr" in tok: return (1.12, 1.12, -100)
    return (1.0, 1.05, 0) if i % 2 == 0 else (1.05, 1.0, 0)

# soft square mask so the stage melts into the frame
_yy, _xx = np.mgrid[0:S, 0:S].astype(np.float32) / S
EDGE = (np.clip(np.minimum.reduce([_xx, 1 - _xx, _yy, 1 - _yy]) / 0.08, 0, 1) ** 1.5)[..., None]

def render_shot(args):
    film, meta, shots, i, nframes, out = args
    random.seed(i)
    sh = shots[i]; tok = sh["tok"]
    base, hot, blobs = scene(film, shots, sh); sprs = blobs + sprites_for(film, sh)
    fxs = [FX[f]() for f in FX if f in tok]; cam = camera(tok, i); hud = HUD(meta)
    fcap = hud.f_cap
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for f in range(nframes):
        t = f / FPS
        cv = base.copy()
        if "glow" in tok and hot is not None:
            cv = np.clip(cv + hot * (0.25 + 0.25 * math.sin(t * 4.2)) * np.array([1.0, 0.45, 0.2], np.float32), 0, 1)
        for sp in sprs: sp.draw(cv, t)
        if fxs:
            ov = Image.new("RGBA", (S, S), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            for fx in fxs: fx.draw(od, t)
            o = np.asarray(ov, np.float32) / 255.0; cv = cv * (1 - o[..., 3:]) + o[..., :3] * o[..., 3:]
        e = smooth(f / max(nframes - 1, 1)); z = cam[0] + (cam[1] - cam[0]) * e
        if abs(z - 1) > 1e-3 or cam[2]:
            sz = int(S * z); img = Image.fromarray((np.clip(cv, 0, 1) * 255).astype(np.uint8)).resize((sz, sz), Image.BILINEAR)
            ox = (sz - S) // 2 - int(cam[2] * (e - 0.5)); ox = min(max(ox, 0), sz - S); oy = (sz - S) // 2
            cv = np.asarray(img, np.float32)[oy:oy + S, ox:ox + S] / 255.0
        fr = hud.plate.copy()
        stage = fr[:, X0:X0 + S]; fr[:, X0:X0 + S] = stage * (1 - EDGE) + np.maximum(cv, stage) * EDGE
        if "flash" in tok and (f < 3 or 10 <= f < 12):
            fr = np.clip(fr + 0.75, 0, 1)
        if "alert" in tok:
            k = 0.5 + 0.5 * math.sin(t * 6)
            fr[:12, :, :] = fr[:12] * 0.3 + np.array(RED, np.float32) / 255 * 0.7 * k
            fr[-12:, :, :] = fr[-12:] * 0.3 + np.array(RED, np.float32) / 255 * 0.7 * k
        if "beat" in tok:                                       # red pulse on each heartbeat, on the stage border only
            c = (t * 1.6) % 1
            if c < 0.15: fr[:, X0:X0 + 8] = np.array(RED, np.float32) / 255; fr[:, X0 + S - 8:X0 + S] = np.array(RED, np.float32) / 255
        im = Image.fromarray((np.clip(fr, 0, 1) * 255).astype(np.uint8)); d = ImageDraw.Draw(im, "RGBA")
        hud.draw(d, t, sh)
        cap = sh["cap"]
        if cap:
            n = min(len(cap), int(t * 40) + 1); txt = cap[:n]          # typed on like a monitor readout
            tw = d.textlength(cap, font=fcap); cx = W // 2
            d.rounded_rectangle([cx - tw / 2 - 30, H - 150, cx + tw / 2 + 30, H - 62], radius=14, fill=(3, 8, 14, 225), outline=CYAN + (200,), width=2)
            d.text((cx - tw / 2, H - 106), txt, font=fcap, fill=WHITE, anchor="lm")
            if n < len(cap) or int(t * 2.5) % 2: d.rectangle([cx - tw / 2 + d.textlength(txt, font=fcap) + 6, H - 130, cx - tw / 2 + d.textlength(txt, font=fcap) + 22, H - 82], fill=CYAN)
        if "endcard" in tok:
            k = back_out((t - 0.5) / 0.6)
            if k > 0.05:
                d.rounded_rectangle([X0 + 560, 330, X0 + 1040, 600], radius=16, outline=CYAN, width=5)
                d.text((X0 + 800, 280), "NEXT PATIENT", font=font(F_BIG, max(8, int(64 * k))), fill=WHITE, anchor="mm")
                d.ellipse([X0 + 690, 660, X0 + 910, 880], outline=RED, width=5)
                d.text((X0 + 800, 920), "SUBSCRIBE", font=font(F_HEAD, 34, 600), fill=RED, anchor="mm")
        ff.stdin.write(im.tobytes())
    ff.stdin.close(); ff.wait(); return out

def tts(text, out):
    subprocess.run([sys.executable, "-m", "piper", "-m", VOICE, "-f", out, "--length-scale", "1.04", "--sentence-silence", "0.28"],
                   input=text.encode(), check=True, capture_output=True)

def render(film, out, limit=None):
    meta, sprites, shots = parse(film)
    if limit: shots = shots[:int(limit)]
    tmp = tempfile.mkdtemp(dir=os.environ.get("TMPDIR")); frames = []; pcm = b""; sr = None
    for i, sh in enumerate(shots):
        p = os.path.join(tmp, f"v{i}.wav"); tts(sh["vo"], p)
        with wave.open(p) as w:
            sr = w.getframerate(); data = w.readframes(w.getnframes())
        n = int(math.ceil((len(data) / 2 / sr + 0.45) * FPS))
        if "endcard" in sh["tok"]: n = max(n, 20 * FPS)
        need = int(round(n / FPS * sr)) * 2; data = data[:need] + b"\0" * max(0, need - len(data))
        pcm += data; frames.append(n)
    audio = os.path.join(tmp, "vo.wav")
    with wave.open(audio, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm)
    jobs = [(film, meta, shots, i, frames[i], os.path.join(tmp, f"s{i:03d}.mp4")) for i in range(len(shots))]
    with Pool(int(os.environ.get("JOBS", os.cpu_count()))) as pool:
        for k, r in enumerate(pool.imap_unordered(render_shot, jobs)): print(f"shot {k + 1}/{len(jobs)}", flush=True)
    lst = os.path.join(tmp, "list.txt"); open(lst, "w").write("".join(f"file '{j[5]}'\n" for j in jobs))
    bed = os.path.join(ROOT, "pipeline", "bed.wav")
    mix = ["-i", bed, "-filter_complex", "[2:a]volume=0.10,aloop=loop=-1:size=2e9[b];[1:a][b]amix=inputs=2:duration=first:normalize=0[a]", "-map", "0:v", "-map", "[a]"] if os.path.exists(bed) else ["-map", "0:v", "-map", "1:a"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", audio, *mix,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    total = sum(frames) / FPS; print(out, f"{total:.1f}s")
    json.dump([{"id": s["id"], "start": round(sum(frames[:k]) / FPS, 2)} for k, s in enumerate(shots)],
              open(os.path.splitext(out)[0] + ".times.json", "w"), indent=0)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "gen": gen(sys.argv[2], sys.argv[3:])
    elif cmd == "render": render(sys.argv[2], sys.argv[3], *(sys.argv[4:5]))
