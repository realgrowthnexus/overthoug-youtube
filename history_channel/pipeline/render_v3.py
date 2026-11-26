"""Cut-out animation test v3. Backdrops stay still; characters are separate layers that enter, breathe,
walk and struggle; particles (soot, birds, smoke) add life. The camera only drifts slowly. No screen shake.
Usage: python3 pipeline/render_v3.py VOICE.onnx OUT.mp4"""
import sys, os, subprocess, wave, math, tempfile, random
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_test import whiten
from layers import split
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(HERE, "..", "style", "fonts", "Kalam-Bold.ttf")
W, H, FPS, S = 1920, 1080, 24, 1080
R = random.Random(7)

def back_out(t, s=1.7):
    t = min(max(t, 0), 1) - 1; return t * t * ((s + 1) * t + s) + 1
def smooth(t): t = min(max(t, 0), 1); return t * t * (3 - 2 * t)
def load(path, size=S): return whiten(Image.open(os.path.join(HERE, path))).resize((size, size), Image.LANCZOS)
def blobs(path, **kw): return split(load(path), **kw)

class Actor:
    def __init__(s, img, x, y, scale=1.0, enter="pop", delay=0.0, idle="breathe", walk_from=None):
        s.img, s.x, s.y, s.scale, s.enter, s.delay, s.idle = img, x, y, scale, enter, delay, idle
        s.walk_from = walk_from; s.ph = R.random()
    @classmethod
    def from_blob(cls, b, **kw):  # keep the blob where it sat in its source picture
        return cls(b["img"], b["x"] + b["w"] / 2, b["y"] + b["h"], **kw)
    def draw(s, cv, t):
        lt = t - s.delay
        if lt < 0 and s.enter != "none": return
        sx = sy = s.scale; ang = dx = dy = 0.0
        if s.enter == "pop":
            k = max(back_out(lt / 0.45), 0.01); sx *= k; sy *= k
        if s.enter in ("walk_left", "walk_right"):           # walks in from off-screen with a step bounce
            k = smooth(lt / 1.4); d = (1 - k) * (S * 0.6) * (-1 if s.enter == "walk_left" else 1)
            dx += d
            if k < 1: dy -= abs(math.sin(lt * 9)) * 14; ang += 3 * math.sin(lt * 9)
        if s.idle == "breathe":
            b = math.sin(2 * math.pi * (t / 2.6 + s.ph)); sy *= 1 + 0.02 * b; sx *= 1 - 0.008 * b
            ang += 1.0 * math.sin(2 * math.pi * (t / 3.9 + s.ph))
        elif s.idle == "bob":
            dy += 8 * math.sin(2 * math.pi * (t / 1.5 + s.ph)); ang += 4 * math.sin(2 * math.pi * (t / 2.2 + s.ph))
        elif s.idle == "struggle":                              # pushes up, slides back down
            c = (t * 1.2 + s.ph) % 1; p = math.sin(math.pi * c) ** 2
            dy -= 26 * p; sy *= 1 + 0.05 * p; sx *= 1 - 0.03 * p; ang += 2.5 * math.sin(2 * math.pi * c)
        elif s.idle == "pulse":
            k = 1 + 0.04 * math.sin(2 * math.pi * (t / 1.3 + s.ph)); sx *= k; sy *= k
        elif s.idle == "wag":
            ang += 5 * math.sin(2 * math.pi * (t / 1.1 + s.ph))
        w, h = s.img.size; nw, nh = max(1, int(w * sx)), max(1, int(h * sy))
        im = s.img.resize((nw, nh), Image.BILINEAR)
        if abs(ang) > 0.05:  # rotate around the feet
            big = Image.new("RGBA", (nw * 2, nh * 2), (0, 0, 0, 0)); big.paste(im, (nw // 2, nh))
            im = big.rotate(ang, resample=Image.BILINEAR, center=(nw, 2 * nh - 1)); ox, oy = s.x - nw, s.y - 2 * nh
        else:
            ox, oy = s.x - nw / 2, s.y - nh
        cv.alpha_composite(im, (int(ox + dx), int(oy + dy)))

# ---------- backdrops & particles drawn in code ----------
def chimney_plate():
    im = Image.new("RGBA", (S, S), (255, 255, 255, 255)); d = ImageDraw.Draw(im)
    L, Rr, wall = 330, 750, 150
    d.rectangle([L, 0, Rr, S], fill=(52, 46, 44, 255))                     # dark shaft
    for x0 in (L - wall, Rr):                                               # brick walls
        d.rectangle([x0, 0, x0 + wall, S], fill=(176, 92, 66, 255))
        for row, y in enumerate(range(0, S, 46)):
            off = 0 if row % 2 else 37
            for x in range(x0 - 74 + off, x0 + wall, 74):
                d.rectangle([max(x, x0), y, min(x + 74, x0 + wall), y + 46], outline=(30, 24, 22, 255), width=4)
        d.line([(x0, 0), (x0, S)], fill=(20, 18, 18, 255), width=7); d.line([(x0 + wall, 0), (x0 + wall, S)], fill=(20, 18, 18, 255), width=7)
    return im
def drop_grey_shadow(img):
    """Remove flat light-grey ground shadow pixels (low saturation, light) from a cut-out."""
    import numpy as np
    a = np.asarray(img).copy(); rgb = a[..., :3].astype(int)
    grey = (rgb.max(2) - rgb.min(2) < 14) & (rgb.mean(2) > 150)
    a[..., 3][grey] = 0
    return Image.fromarray(a, "RGBA")
def floor_plate():
    im = Image.new("RGBA", (S, S), (255, 255, 255, 255)); d = ImageDraw.Draw(im)
    d.line([(40, 962), (S - 40, 966)], fill=(30, 30, 30, 255), width=6)            # hand-drawn floor line
    return im
class Soot:
    def __init__(s, n=45, x0=345, x1=735):
        s.p = [[R.uniform(x0, x1), R.uniform(-S, S), R.uniform(40, 110), R.uniform(3, 8)] for _ in range(n)]
    def draw(s, cv, t):
        d = ImageDraw.Draw(cv)
        for x, y, v, r in s.p:
            yy = (y + v * t) % S; d.ellipse([x - r, yy - r, x + r, yy + r], fill=(20, 18, 18, 255))
class Puffs:  # dust puffs when the boy pushes up
    def __init__(s, x, y): s.x, s.y = x, y
    def draw(s, cv, t):
        c = (t * 1.2) % 1; d = ImageDraw.Draw(cv)
        if c < 0.5:
            for k in (-1, 1):
                r = 10 + 50 * c; a = int(200 * (1 - c * 2))
                d.ellipse([s.x + k * (140 + 80 * c) - r, s.y - r, s.x + k * (140 + 80 * c) + r, s.y + r], outline=(30, 30, 30, a), width=5)
class Birds:
    def __init__(s, n=5): s.b = [[R.uniform(-300, 200), R.uniform(150, 400), R.uniform(70, 120), R.random()] for _ in range(n)]
    def draw(s, cv, t):
        d = ImageDraw.Draw(cv)
        for x, y, v, ph in s.b:
            xx = x + v * t; f = 10 * math.sin(2 * math.pi * (t * 3 + ph))
            d.line([(xx - 18, y - f), (xx, y), (xx + 18, y - f)], fill=(25, 25, 25, 255), width=4, joint="curve")
class Flame:
    def __init__(s, x, y): s.x, s.y = x, y
    def draw(s, cv, t):
        h = 26 + 6 * math.sin(t * 13) + 4 * math.sin(t * 7.3); d = ImageDraw.Draw(cv)
        d.ellipse([s.x - 9, s.y - h, s.x + 9, s.y], fill=(255, 190, 40, 230)); d.ellipse([s.x - 4, s.y - h * 0.6, s.x + 4, s.y], fill=(255, 245, 180, 255))

# ---------- shots ----------
def build():
    b02 = blobs("scenes/02.jpg")                  # boy, sweat drop, soot pile
    boy02 = Actor.from_blob(b02[0], enter="pop", idle="breathe")
    extra02 = [Actor.from_blob(b, enter="pop", delay=0.4, idle="bob") for b in b02[1:]]
    crouch = blobs("layers/L_boy_crouch.jpg", tol=200)[0]
    crouch["img"] = drop_grey_shadow(crouch["img"])
    plate = chimney_plate()
    def chim(idle):
        a = Actor(crouch["img"], 540, 760, scale=min(1.0, 380 / crouch["w"]), enter="none", idle=idle); return a
    london = load("scenes/03.jpg").convert("RGBA")
    room = load("layers/L_room.jpg").convert("RGBA")
    pars = sorted(blobs("layers/L_parents.jpg")[:2], key=lambda b: b["x"])
    kids = sorted([b for b in blobs("layers/L_kids.jpg", tol=35) if b["area"] > 2000], key=lambda b: b["x"])
    b05 = blobs("scenes/05.jpg")
    scroll = blobs("layers/L_scroll.jpg")[0]; offi = blobs("layers/L_official.jpg")[0]
    kid_imgs = [k["img"] for k in kids]
    room_actors = [Actor(p["img"], 660 + j * 210, 960, scale=0.8, enter="walk_right", delay=0.15 * j, idle="breathe") for j, p in enumerate(pars)] + \
                  [Actor(img, 170 + i * 105, 960, scale=1.55, enter="pop", delay=0.6 + 0.2 * i, idle="breathe") for i, img in enumerate(kid_imgs)]
    law = [Actor(scroll["img"], 640, 900, scale=0.95, enter="pop", idle="breathe"),
           Actor(offi["img"], 290, 1000, scale=0.75, enter="walk_left", delay=0.3, idle="breathe")]
    law2 = [Actor(scroll["img"], 640, 900, scale=0.95, enter="none", idle="breathe"),
            Actor(offi["img"], 290, 1000, scale=0.75, enter="none", idle="wag")]
    return [
     # narration, caption, backdrop, layers, camera(zoom0, zoom1, panx)
     ("You are seven years old.", "7 years old", None, [boy02] + extra02, (1.0, 1.05, 0)),
     ("You're inside a chimney, in the dark. The tunnel around you is about the width of a dinner plate, and your knees are pressed up against your chin.",
      None, plate, [Soot(), chim("breathe")], (1.0, 1.1, 0)),
     ("You can't go up. And you can't go down.", None, plate, [Soot(), Puffs(540, 760), chim("struggle")], (1.1, 1.22, 0)),
     ("Let's go back to how you got here.", "London, 1862", london, [Birds()], (1.12, 1.12, -100)),
     ("London, eighteen sixty-two. You arrive in a single rented room, shared with your parents and four siblings,", None, floor_plate(),
      room_actors, (1.0, 1.05, 0)),
     ("and a damp patch on the wall that has more personality than your dad.", None, None,
      [Actor.from_blob(b05[0], enter="pop", idle="pulse")] + [Actor.from_blob(b, enter="pop", delay=0.3, idle="breathe") for b in b05[1:2]], (1.0, 1.05, 0)),
     ("Fun fact about eighteen sixty-two. A law passed twenty-two years before you were born already says nobody under twenty-one is allowed to climb a chimney.",
      "1840 law: no climbing under 21", None, law, (1.0, 1.05, 0)),
     ("Hold on to that. It's going to be hilarious later.", None, None, law2, (1.05, 1.12, 0)),
    ]

def main(voice, out):
    shots = build(); tmp = tempfile.mkdtemp(); wavs = []; durs = []
    for i, sh in enumerate(shots):
        p = os.path.join(tmp, f"{i}.wav")
        subprocess.run([sys.executable, "-m", "piper", "-m", voice, "-f", p, "--length-scale", "1.05", "--sentence-silence", "0.2"],
                       input=sh[0].encode(), check=True, capture_output=True)
        with wave.open(p) as w: durs.append(w.getnframes() / w.getframerate() + 0.35); sr = w.getframerate()
        wavs.append(p)
    pad = os.path.join(tmp, "pad.wav"); lst = os.path.join(tmp, "a.txt"); audio = os.path.join(tmp, "v.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"anullsrc=r={sr}:cl=mono", "-t", "0.35", pad], check=True)
    open(lst, "w").write("".join(f"file '{p}'\nfile '{pad}'\n" for p in wavs))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", audio], check=True)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", audio, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-c:a", "aac", "-shortest", out], stdin=subprocess.PIPE)
    font = ImageFont.truetype(FONT, 72)
    for (txt, cap, bd, lays, cam), d in zip(shots, durs):
        bg = bd if bd is not None else Image.new("RGBA", (S, S), (255, 255, 255, 255)); n = int(d * FPS)
        for f in range(n):
            t = f / FPS; cv = bg.copy()
            for l in lays: l.draw(cv, t)
            e = smooth(f / max(n - 1, 1)); z = cam[0] + (cam[1] - cam[0]) * e
            sz = int(S * z); img = cv.convert("RGB").resize((sz, sz), Image.BILINEAR)
            fr = Image.new("RGB", (W, H), "white"); fr.paste(img, ((W - sz) // 2 + int(cam[2] * e), (H - sz) // 2))
            if cap:
                k = back_out(f / (0.4 * FPS)); dr = ImageDraw.Draw(fr)
                dr.text((W // 2, 95), cap, font=ImageFont.truetype(FONT, max(8, int(72 * k))), fill="black", anchor="mm")
                if f > 0.4 * FPS:
                    u = smooth((f - 0.4 * FPS) / (0.4 * FPS)); tw = dr.textlength(cap, font=font)
                    dr.line([(W // 2 - tw / 2, 140), (W // 2 - tw / 2 + tw * u, 140)], fill="black", width=5)
            ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait(); print(out, round(sum(durs), 1), "s")
if __name__ == "__main__": main(sys.argv[1], sys.argv[2])
