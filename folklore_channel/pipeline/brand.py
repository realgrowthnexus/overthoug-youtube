"""Channel branding for The Ward Book: avatar (800x800), banner (2560x1440, text inside the 1546x423 safe area),
watermark (150x150). Usage: python3 pipeline/brand.py"""
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wardlib as L
from layers import split
from thumbs import lit_paper, BONE, VERM
B = os.path.join(L.ROOT, "branding")
NIGHT = (16, 12, 10)

def avatar():
    A = 800; base = Image.new("RGB", (A, A), "white"); d = ImageDraw.Draw(base)
    d.text((A // 2, A // 2 + 30), "W", font=L.font(L.F_BLACK, 470), fill=L.OCHRE, anchor="mm")
    for r, w in ((300, 6), (282, 2)): d.ellipse([A / 2 - r, A / 2 - r, A / 2 + r, A / 2 + r], outline=L.INK, width=w)
    for k in range(4):                                             # four small diamonds on the ring
        a = math.pi / 4 + k * math.pi / 2; x, y = A / 2 + 291 * math.cos(a), A / 2 + 291 * math.sin(a)
        d.polygon([(x, y - 14), (x + 14, y), (x, y + 14), (x - 14, y)], fill=L.INK)
    a = np.asarray(base, np.float32) / 255 * lit_paper(A, A, A / 2, A / 2, 420, 420, dark=0.97)
    im = Image.fromarray((a.clip(0, 1) * 255).astype(np.uint8))
    im.save(os.path.join(B, "avatar_800.png"))
    im.resize((150, 150), Image.LANCZOS).save(os.path.join(B, "watermark_150.png"))

def cut(path, h):
    b = split(L.whiten(Image.open(path)).resize((1024, 1024)))[0]["img"]; b = b.crop(b.getbbox())
    return b.resize((int(b.width * h / b.height), h), Image.LANCZOS)

def banner():
    Wb, Hb = 2560, 1440; sx0, sy0, sw, sh = (Wb - 1546) // 2, (Hb - 423) // 2, 1546, 423
    base = Image.new("RGBA", (Wb, Hb), (255, 255, 255, 255)); d = ImageDraw.Draw(base)
    E = os.path.join(L.ROOT, "episodes")
    figs = [("ep04/img/h07.jpg", 380, 200), ("ep01/img/k03.jpg", 400, 470), ("ep03/img/b05.jpg", 330, 2100), ("ep02/img/w03.jpg", 420, 2390)]
    for p, h, x in figs:
        f = cut(os.path.join(E, p), h); base.alpha_composite(f, (int(x - f.width / 2), sy0 + sh - h + 20))
    cx = Wb // 2
    d.text((cx, sy0 + 70), "How to survive the monsters of world folklore", font=L.font(L.F_SC, 46), fill=L.INK, anchor="mm")
    d.text((cx, sy0 + 195), "The Ward Book", font=L.font(L.F_BLACK, 168), fill=L.OCHRE, anchor="mm")
    L.ornament(d, cx, sy0 + 295, 620)
    d.text((cx, sy0 + 350), "Every legend comes with rules. New ward every Wednesday.", font=L.font(L.F_ITAL, 48), fill=L.INK, anchor="mm")
    a = np.asarray(base.convert("RGB"), np.float32) / 255 * lit_paper(Wb, Hb, cx, Hb / 2, 1350, 330, dark=0.95)
    Image.fromarray((a.clip(0, 1) * 255).astype(np.uint8)).save(os.path.join(B, "banner_2560x1440.png"))

if __name__ == "__main__":
    avatar(); banner()
