"""Shared look for The Ward Book: background cleanup, cut-out actors with an ink-bleed entrance, particles,
the parchment + candle-light finish, and the fonts and colours. Adapted from history_channel/pipeline
(render_test.whiten, render_v3.Actor), restyled for a woodcut-on-parchment look."""
import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "fonts")
F_TEXT = os.path.join(FONTS, "IMFellEnglish-Regular.ttf")
F_ITAL = os.path.join(FONTS, "IMFellEnglish-Italic.ttf")
F_SC = os.path.join(FONTS, "IMFellEnglishSC-Regular.ttf")
F_BLACK = os.path.join(FONTS, "UnifrakturMaguntia.ttf")
F_BOLD = os.path.join(FONTS, "Cinzel-Bold.ttf")
INK = (24, 18, 14)            # iron-gall black
OCHRE = (150, 36, 22)         # rubric red (the one accent colour)
EMBER = (226, 150, 60)        # candle amber, used for light only
PAPER = (236, 222, 190)
NIGHT = (14, 12, 10)
W, H, FPS, S = 1920, 1080, 24, 1080
R = random.Random(7)
_fonts = {}
def font(path, size):
    k = (path, int(size))
    if k not in _fonts: _fonts[k] = ImageFont.truetype(path, max(6, int(size)))
    return _fonts[k]

def back_out(t, s=1.7):
    t = min(max(t, 0), 1) - 1; return t * t * ((s + 1) * t + s) + 1
def smooth(t): t = min(max(t, 0), 1); return t * t * (3 - 2 * t)

def whiten(im, tol=34):
    """Turn only the backdrop white: pixels close to the edge colour AND connected to the border."""
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    edge = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]); bg = np.median(edge, axis=0)
    close = np.abs(a - bg).sum(2) <= tol
    lab, _ = ndimage.label(close)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])).tolist()) - {0}
    mask = ndimage.gaussian_filter(np.isin(lab, list(border)).astype(np.float32), 1.2)[..., None]
    return Image.fromarray((a * (1 - mask) + 255 * mask).clip(0, 255).astype(np.uint8))

# ---------- actors ----------
def _noise(w, h, seed):
    g = np.random.default_rng(seed).random((max(2, h // 12), max(2, w // 12))).astype(np.float32)
    n = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)).astype(np.float32) / 255
    return (n - n.min()) / max(1e-6, n.max() - n.min())

class Actor:
    """A cut-out that bleeds in like wet ink (or walks in), then idles: breathe, sway, loom, creep, bob, pulse,
    struggle, wag, flicker. Pivot is the bottom-centre (x, y)."""
    def __init__(s, img, x, y, scale=1.0, enter="ink", delay=0.0, idle="breathe"):
        s.img, s.x, s.y, s.scale, s.enter, s.delay, s.idle = img, x, y, scale, enter, delay, idle
        s.ph = R.random(); s._noise = None
    @classmethod
    def from_blob(cls, b, **kw): return cls(b["img"], b["x"] + b["w"] / 2, b["y"] + b["h"], **kw)
    def _ink(s, im, k):
        if s._noise is None or s._noise.shape != (im.height, im.width): s._noise = _noise(im.width, im.height, int(s.ph * 1e6))
        a = np.asarray(im).copy(); m = np.clip((k * 1.35 - s._noise) * 6, 0, 1)
        a[..., 3] = (a[..., 3] * m).astype(np.uint8); return Image.fromarray(a, "RGBA")
    def draw(s, cv, t):
        lt = t - s.delay
        if lt < 0 and s.enter != "none": return
        sx = sy = s.scale; ang = dx = dy = 0.0
        if s.enter in ("walk_left", "walk_right"):
            k = smooth(lt / 1.6); dx += (1 - k) * (S * 0.6) * (-1 if s.enter == "walk_left" else 1)
            if k < 1: dy -= abs(math.sin(lt * 7)) * 10; ang += 2 * math.sin(lt * 7)
        if s.idle == "breathe":
            b = math.sin(2 * math.pi * (t / 3.2 + s.ph)); sy *= 1 + 0.015 * b; sx *= 1 - 0.006 * b
            ang += 0.6 * math.sin(2 * math.pi * (t / 4.5 + s.ph))
        elif s.idle == "sway":                                   # hanging things, trees, lanterns
            ang += 3 * math.sin(2 * math.pi * (t / 3.0 + s.ph))
        elif s.idle == "loom":                                   # creeps toward the viewer
            k = 1 + 0.10 * smooth(t / 6); sx *= k; sy *= k
        elif s.idle == "creep":                                  # slides slowly sideways
            dx += 60 * smooth(t / 6) * (1 if s.ph > 0.5 else -1)
        elif s.idle == "bob":
            dy += 7 * math.sin(2 * math.pi * (t / 1.7 + s.ph)); ang += 3 * math.sin(2 * math.pi * (t / 2.4 + s.ph))
        elif s.idle == "struggle":
            c = (t * 1.1 + s.ph) % 1; p = math.sin(math.pi * c) ** 2
            dy -= 18 * p; sy *= 1 + 0.04 * p; sx *= 1 - 0.02 * p; ang += 2 * math.sin(2 * math.pi * c)
        elif s.idle == "pulse":
            k = 1 + 0.035 * math.sin(2 * math.pi * (t / 1.4 + s.ph)); sx *= k; sy *= k
        elif s.idle == "wag":
            ang += 4 * math.sin(2 * math.pi * (t / 1.2 + s.ph))
        elif s.idle == "shiver":
            dx += 2.5 * math.sin(t * 41 + s.ph * 9); ang += 0.8 * math.sin(t * 37)
        w, h = s.img.size; nw, nh = max(1, int(w * sx)), max(1, int(h * sy))
        im = s.img.resize((nw, nh), Image.BILINEAR)
        if s.enter == "ink" and lt < 0.9: im = s._ink(im, smooth(lt / 0.9))
        if abs(ang) > 0.05:
            big = Image.new("RGBA", (nw * 2, nh * 2), (0, 0, 0, 0)); big.paste(im, (nw // 2, nh))
            im = big.rotate(ang, resample=Image.BILINEAR, center=(nw, 2 * nh - 1)); ox, oy = s.x - nw, s.y - 2 * nh
        else:
            ox, oy = s.x - nw / 2, s.y - nh
        cv.alpha_composite(im, (int(ox + dx), int(oy + dy)))

# ---------- particles (drawn on the square art canvas, before the parchment multiply) ----------
class Snow:
    def __init__(s, n=90):
        g = random.Random(3); s.p = [[g.uniform(0, S), g.uniform(0, S), g.uniform(40, 110), g.uniform(2, 6), g.random()] for _ in range(n)]
    def draw(s, cv, t):
        d = ImageDraw.Draw(cv)
        for x, y, v, r, ph in s.p:
            yy = (y + v * t) % S; xx = x + 18 * math.sin(t * 1.3 + ph * 7)
            d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(120, 110, 100, 150))
class Dust:                     # motes drifting in candle light
    def __init__(s, n=40):
        g = random.Random(4); s.p = [[g.uniform(0, S), g.uniform(0, S), g.uniform(6, 18), g.random()] for _ in range(n)]
    def draw(s, cv, t):
        d = ImageDraw.Draw(cv)
        for x, y, v, ph in s.p:
            yy = (y - v * t) % S; xx = x + 25 * math.sin(t * 0.7 + ph * 6); a = int(90 + 80 * math.sin(t * 2 + ph * 9))
            d.ellipse([xx - 2, yy - 2, xx + 2, yy + 2], fill=INK + (max(0, a),))
class Embers:
    def __init__(s, n=36):
        g = random.Random(5); s.p = [[g.uniform(0, S), g.uniform(0, S), g.uniform(40, 90), g.random()] for _ in range(n)]
    def draw(s, cv, t):
        d = ImageDraw.Draw(cv)
        for x, y, v, ph in s.p:
            yy = (y - v * t) % S; xx = x + 20 * math.sin(t * 2 + ph * 6); r = 3 + 2 * math.sin(t * 5 + ph * 9)
            d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=OCHRE + (230,))
class Fog:                      # hatched mist bands drifting across the bottom
    def __init__(s, n=7):
        g = random.Random(6); s.p = [[g.uniform(-200, S), g.uniform(S * 0.6, S * 0.95), g.uniform(15, 35), g.uniform(160, 320)] for _ in range(n)]
    def draw(s, cv, t):
        d = ImageDraw.Draw(cv)
        for x, y, v, w in s.p:
            xx = (x + v * t) % (S + 400) - 200
            for k in range(5): d.arc([xx - w, y - 30 + k * 7, xx + w, y + 30 + k * 7], 200, 340, fill=INK + (70,), width=2)
class Bats:
    def __init__(s, n=6):
        g = random.Random(8); s.b = [[g.uniform(-300, 200), g.uniform(120, 420), g.uniform(90, 150), g.random()] for _ in range(n)]
    def draw(s, cv, t):
        d = ImageDraw.Draw(cv)
        for x, y, v, ph in s.b:
            xx = x + v * t; yy = y + 25 * math.sin(t * 2 + ph * 5); f = 12 * math.sin(2 * math.pi * (t * 4 + ph))
            d.line([(xx - 22, yy - f), (xx - 8, yy - 4), (xx, yy + 2), (xx + 8, yy - 4), (xx + 22, yy - f)], fill=INK + (255,), width=4, joint="curve")
class Wind:                     # streaks of wind for the hunt
    def __init__(s, n=22):
        g = random.Random(12); s.p = [[g.uniform(0, S), g.uniform(0, S), g.uniform(500, 900), g.uniform(60, 160)] for _ in range(n)]
    def draw(s, cv, t):
        d = ImageDraw.Draw(cv)
        for x, y, v, l in s.p:
            xx = (x + v * t) % (S + 300) - 150; d.line([(xx, y), (xx + l, y - l * 0.12)], fill=INK + (110,), width=2)
class Rain:
    def __init__(s, n=70):
        g = random.Random(3); s.p = [[g.uniform(0, S), g.uniform(0, S), g.uniform(500, 800)] for _ in range(n)]
    def draw(s, cv, t):
        d = ImageDraw.Draw(cv)
        for x, y, v in s.p:
            yy = (y + v * t) % S; d.line([(x, yy), (x - 6, yy + 26)], fill=INK + (150,), width=2)
class Flame:
    def __init__(s, x, y): s.x, s.y = x, y
    def draw(s, cv, t):
        h = 30 + 7 * math.sin(t * 13) + 4 * math.sin(t * 7.3); d = ImageDraw.Draw(cv)
        d.ellipse([s.x - 10, s.y - h, s.x + 10, s.y], fill=OCHRE + (230,)); d.ellipse([s.x - 4, s.y - h * 0.6, s.x + 4, s.y], fill=(255, 240, 200, 255))
FX = {"snow": Snow, "dust": Dust, "embers": Embers, "fog": Fog, "bats": Bats, "wind": Wind, "rain": Rain}

# ---------- parchment + candle light ----------
_paper = None
def paper():
    """Full-frame aged parchment (float32, 0-1) and an edge mask for the candle vignette."""
    global _paper
    if _paper is None:
        cache = os.path.join(ROOT, "pipeline", ".paper.npz")
        if os.path.exists(cache):
            z = np.load(cache); _paper = (z["p"], z["e"])
        else:
            g = np.random.default_rng(11)
            def blur_noise(scale, sigma):
                n = g.random((H // scale + 2, W // scale + 2)).astype(np.float32)
                n = np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)).astype(np.float32) / 255
                return ndimage.gaussian_filter(n, sigma)
            blot = 0.55 * blur_noise(60, 20) + 0.3 * blur_noise(14, 4) + 0.15 * g.random((H, W)).astype(np.float32)
            base = np.array(PAPER, np.float32) / 255
            tone = 1 - 0.10 * (blot - blot.mean()) / blot.std() * 0.5
            p = base[None, None, :] * tone[..., None]
            # fibres
            fib = Image.new("L", (W, H), 0); d = ImageDraw.Draw(fib)
            for _ in range(500):
                x, y = g.uniform(0, W), g.uniform(0, H); a = g.uniform(0, math.pi); l = g.uniform(8, 40)
                d.line([(x, y), (x + l * math.cos(a), y + l * math.sin(a))], fill=int(g.uniform(15, 40)), width=1)
            p *= (1 - np.asarray(fib, np.float32)[..., None] / 255 * 0.5)
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.70)) ** 2)
            e = np.clip(r - 0.45, 0, None) ** 1.6 * 1.9
            e = np.clip(e + 0.05 * (blot - 0.5), 0, 1)
            _paper = (p.astype(np.float32), e.astype(np.float32))
            np.savez_compressed(cache, p=_paper[0], e=_paper[1])
    return _paper

def finish(frame, t, dark=0.0):
    """Multiply the white-paper frame onto parchment and darken the edges like candle light (gentle flicker).
    dark: 0 normal, up to 1 for a near-black night shot."""
    p, e = paper()
    fl = 0.62 + 0.06 * math.sin(t * 7.1) + 0.04 * math.sin(t * 12.7 + 1.3) + 0.03 * math.sin(t * 3.3)
    light = 1 - np.clip(e * (fl + 0.9 * dark) + 0.25 * dark, 0, 0.96)
    a = np.asarray(frame, np.float32) / 255
    out = a * p * light[..., None]
    # warm the light a little where the candle reaches
    out[..., 0] *= 1.02; out[..., 2] *= 0.97
    return Image.fromarray((out.clip(0, 1) * 255).astype(np.uint8))

def wrap(d, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        nxt = (cur + " " + w_).strip()
        if d.textlength(nxt, font=fnt) <= width: cur = nxt
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

def ornament(d, cx, y, w, col=INK, width=3):
    """A printer's rule with a diamond in the middle."""
    d.line([(cx - w / 2, y), (cx - 18, y)], fill=col, width=width); d.line([(cx + 18, y), (cx + w / 2, y)], fill=col, width=width)
    d.polygon([(cx, y - 9), (cx + 10, y), (cx, y + 9), (cx - 10, y)], fill=OCHRE)
