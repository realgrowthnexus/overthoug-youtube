"""Your Vitals branding: avatar (800x800), banner (2560x1440, text inside the 1546x423 safe area), watermark (150x150).
Usage: python3 pipeline/brand.py"""
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); B = os.path.join(ROOT, "branding")
F_BIG = os.path.join(ROOT, "fonts", "Anton-Regular.ttf"); F_MONO = os.path.join(ROOT, "fonts", "JetBrainsMono[wght].ttf")
BG, CYAN, RED, HOT, WHITE = (3, 5, 10), (70, 225, 255), (255, 59, 59), (255, 122, 26), (245, 250, 255)

def neon(path, box=None):
    a = np.asarray(Image.open(path).convert("RGB"), np.float32) / 255
    a = a * np.clip((a.max(2, keepdims=True) - 0.06) / 0.1, 0, 1)
    ys, xs = np.where(a.max(2) > 0.18); a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return a
def screen(base, arr, x, y):
    h, w = arr.shape[:2]; reg = base[y:y + h, x:x + w]; base[y:y + h, x:x + w] = 1 - (1 - reg) * (1 - arr[:reg.shape[0], :reg.shape[1]])
def resize(arr, h):
    im = Image.fromarray((arr * 255).astype(np.uint8)); w = int(im.width * h / im.height)
    return np.asarray(im.resize((w, h), Image.LANCZOS), np.float32) / 255
def grid(d, W, H, step, col=(9, 14, 22)):
    for x in range(0, W, step): d.line([(x, 0), (x, H)], fill=col)
    for y in range(0, H, step): d.line([(0, y), (W, y)], fill=col)
def ecg(d, x0, x1, y, period, amp, col, width):
    pts = []
    for x in range(x0, x1):
        ph = ((x - x0) / period) % 1
        dy = -amp if 0.40 < ph < 0.43 else amp * 0.45 if 0.43 < ph < 0.46 else -amp * 0.15 if 0.62 < ph < 0.70 else 0
        pts.append((x, y + dy))
    d.line(pts, fill=col, width=width)
def glow_text(c, xy, txt, font, col, anchor="mm", blur=18):
    g = Image.new("RGBA", c.size, (0, 0, 0, 0)); ImageDraw.Draw(g).text(xy, txt, font=font, fill=col + (230,), anchor=anchor)
    g = g.filter(ImageFilter.GaussianBlur(blur)); c.paste(g, (0, 0), g); ImageDraw.Draw(c).text(xy, txt, font=font, fill=col, anchor=anchor)

def avatar():
    A = 800; c = Image.new("RGB", (A, A), BG); d = ImageDraw.Draw(c); grid(d, A, A, 50)
    you = neon(os.path.join(ROOT, "episodes", "ep01", "img", "spr_you.jpg"))
    head = you[: int(you.shape[0] * 0.42)]                         # head + shoulders + glowing heart
    head = resize(head, 560); base = np.asarray(c, np.float32) / 255
    screen(base, head, (A - head.shape[1]) // 2, A - 560 - 40); c = Image.fromarray((base * 255).astype(np.uint8)); d = ImageDraw.Draw(c)
    ecg(d, 40, A - 40, 690, 380, 70, RED, 9)
    d.ellipse([22, 22, A - 22, A - 22], outline=CYAN, width=12)
    c.save(os.path.join(B, "avatar_800.png"))

def watermark():
    S = 600; c = Image.new("RGB", (S, S), BG); d = ImageDraw.Draw(c)
    d.rounded_rectangle([20, 20, S - 20, S - 20], radius=110, outline=CYAN, width=26)
    ecg(d, 70, S - 70, 330, 460, 170, RED, 34)
    c.resize((150, 150), Image.LANCZOS).save(os.path.join(B, "watermark_150.png"))

def banner():
    Wb, Hb = 2560, 1440; c = Image.new("RGB", (Wb, Hb), BG); d = ImageDraw.Draw(c); grid(d, Wb, Hb, 64)
    sx0, sy0, sw, sh = (Wb - 1546) // 2, (Hb - 423) // 2, 1546, 423
    ecg(d, 0, Wb, sy0 + sh - 8, 640, 70, (40, 120, 140), 6)           # monitor line runs edge to edge
    base = np.asarray(c, np.float32) / 255
    figs = [("ep01", "spr_tired"), ("ep03", "spr_fried"), ("ep04", "spr_full"), ("ep01", "spr_you")]
    xs = [sx0 + 90, sx0 + 250, sx0 + sw - 250, sx0 + sw - 90]
    for (ep, f), x in zip(figs, xs):
        p = os.path.join(ROOT, "episodes", ep, "img", f + ".jpg")
        if not os.path.exists(p): continue
        a = resize(neon(p), 330); screen(base, a, int(x - a.shape[1] / 2), sy0 + sh - 345)
    c = Image.fromarray((base * 255).astype(np.uint8))
    glow_text(c, (Wb // 2, sy0 + 120), "YOUR VITALS", ImageFont.truetype(F_BIG, 170), WHITE)
    fm = ImageFont.truetype(F_MONO, 40)
    try: fm.set_variation_by_axes([600])
    except Exception: pass
    d = ImageDraw.Draw(c)
    d.text((Wb // 2, sy0 + 262), "What happens to your body if…", font=fm, fill=CYAN, anchor="mm")
    d.text((Wb // 2, sy0 + 322), "● NEW PATIENT EVERY WEDNESDAY", font=fm, fill=RED, anchor="mm")
    c.save(os.path.join(B, "banner_2560x1440.png"))

if __name__ == "__main__":
    os.makedirs(B, exist_ok=True); avatar(); watermark(); banner(); print("branding done")
