"""Your Vitals thumbnails (1280x720): neon art on the left, 2 lines of huge condensed text on the right,
one hot word in orange/red, plus a vitals chip (the channel's signature).
Usage: python3 pipeline/thumbs.py gen [ids]   (art, ~$0.012 each)   |   python3 pipeline/thumbs.py compose"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); T = os.path.join(ROOT, "thumbs")
F_BIG = os.path.join(ROOT, "fonts", "Anton-Regular.ttf"); F_MONO = os.path.join(ROOT, "fonts", "JetBrainsMono[wght].ttf")
THUMB = ("glowing neon line art illustration on a pure solid black background, like a medical hologram or x-ray scan, "
         "luminous cyan outlines, danger spots glow hot orange and red, high contrast, dramatic, bold, centered on the left, no text, no letters, no numbers, ")
HOT, WHITE, CYAN, RED, GREEN = (255, 122, 26), (245, 250, 255), (70, 225, 255), (255, 59, 59), (56, 242, 155)
# out: (art, line1, line2, chip, chip colour, hot line index)
PLAN = {
    "EP01_A": ("T01a", "264 HOURS", "NO SLEEP", "HR 96  ● CRITICAL", RED, 1),
    "EP01_B": ("T01b", "17 HOURS", "= DRUNK", "BRAIN ≈ 0.05% BAC", HOT, 1),
    "EP02_A": ("T02a", "11 KM", "DOWN", "DEPTH -10,935 m  ● FLATLINE", RED, 1),
    "EP02_B": ("T02b", "8 TONNES", "PER INCH", "PRESSURE 1,100 atm", RED, 0),
    "EP03_A": ("T03a", "90% SURVIVE.", "THEN WHAT?", "HR 0  ● ASYSTOLE", RED, 1),
    "EP03_B": ("T03b", "SCANS SAY", "\"NORMAL\"", "NERVE DAMAGE  ● HIDDEN", HOT, 1),
    "EP04_A": ("T04a", "LIVER", "ALARM", "ALT ▲▲▲  DAY 21", RED, 1),
    "EP04_B": ("T04b", "IT STAYS", "FOR YEARS", "+3.1 kg  @ 2.5 YEARS", HOT, 1),
}
def fit(d, text, w, h, start=230):
    s = start
    while s > 40:
        f = ImageFont.truetype(F_BIG, s); b = d.textbbox((0, 0), text, font=f)
        if b[2] - b[0] <= w and b[3] - b[1] <= h: return f
        s -= 4
    return ImageFont.truetype(F_BIG, 40)
def thumb(art, out, l1, l2, chip, ccol, hot):
    W, H = 1280, 720
    c = Image.new("RGB", (W, H), (3, 5, 10)); d = ImageDraw.Draw(c)
    for x in range(0, W, 40): d.line([(x, 0), (x, H)], fill=(8, 13, 20))
    for y in range(0, H, 40): d.line([(0, y), (W, y)], fill=(8, 13, 20))
    a = np.asarray(Image.open(art).convert("RGB"), np.float32) / 255
    a = a * np.clip((a.max(2, keepdims=True) - 0.05) / 0.1, 0, 1)
    ys, xs = np.where(a.max(2) > 0.12)                              # crop to the subject, then fill the left side
    a = a[max(ys.min() - 20, 0):ys.max() + 20, max(xs.min() - 20, 0):xs.max() + 20]
    h, w = a.shape[:2]; k = min(700 / h, 680 / w)
    im = Image.fromarray((a * 255).astype(np.uint8)).resize((int(w * k), int(h * k)), Image.LANCZOS)
    pad = Image.new("RGB", (720, 720), (0, 0, 0)); pad.paste(im, ((700 - im.width) // 2 + 10, (720 - im.height) // 2))
    arr = np.asarray(pad, np.float32) / 255
    arr = np.clip(arr * 1.15, 0, 1)                                # punchier than the video frames
    base = np.asarray(c, np.float32) / 255; reg = base[:, 0:720]
    base[:, 0:720] = 1 - (1 - reg) * (1 - arr); c = Image.fromarray((base * 255).astype(np.uint8)); d = ImageDraw.Draw(c)
    x0, tw = 690, 560
    for i, (txt, y, hh) in enumerate(((l1, 70, 200), (l2, 290, 230))):
        f = fit(d, txt, tw, hh); col = HOT if i == hot else WHITE
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
        gd.text((x0, y), txt, font=f, fill=(col if i == hot else CYAN) + (200,))
        c.paste(glow.filter(ImageFilter.GaussianBlur(14)), (0, 0), glow.filter(ImageFilter.GaussianBlur(14)))
        d.text((x0, y), txt, font=f, fill=col, stroke_width=4, stroke_fill=(0, 0, 0))
    # vitals chip with an ECG line
    fm = ImageFont.truetype(F_MONO, 30)
    try: fm.set_variation_by_axes([700])
    except Exception: pass
    cw = d.textlength(chip, font=fm) + 40
    d.rounded_rectangle([x0, 570, x0 + cw, 630], radius=12, fill=(10, 4, 6), outline=ccol, width=4)
    d.text((x0 + 20, 600), chip, font=fm, fill=ccol, anchor="lm")
    pts = []; 
    for i in range(0, 560):
        ph = (i / 140) % 1; y = 662 + (-26 if 0.4 < ph < 0.44 else 14 if 0.44 < ph < 0.48 else 0)
        pts.append((x0 + i, y))
    d.line(pts, fill=ccol, width=4)
    c.save(out, quality=92)
if __name__ == "__main__":
    if sys.argv[1] == "gen":
        import gen as G
        G.STYLE = THUMB
        sc = G.load(os.path.join(T, "thumb_art.txt")); ids = sys.argv[2:] or list(sc)
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(6) as ex:
            for r in ex.map(G.run, [(k, sc[k], T) for k in ids]): print(r, flush=True)
    else:
        for out, (art, l1, l2, chip, ccol, hot) in PLAN.items():
            p = os.path.join(T, art + ".jpg")
            if os.path.exists(p): thumb(p, os.path.join(T, out + ".jpg"), l1, l2, chip, ccol, hot); print(out)
