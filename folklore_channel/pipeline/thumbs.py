"""Ward Book thumbnails (1280x720): candle-lit parchment spot on the left with woodcut art, dark edges,
2 lines of text on the right (small bone-white line + big vermilion punch line).
Usage: python3 pipeline/thumbs.py gen [ids]   (art, ~$0.012 each)  |  python3 pipeline/thumbs.py compose"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wardlib as L
T = os.path.join(L.ROOT, "thumbs")
BONE, VERM = (242, 230, 204), (222, 72, 44)
THUMB = ("old european woodcut print, 16th century engraving style, bold black ink lines, crosshatching, black ink with deep red accents, "
         "dramatic composition, isolated on plain pure white background, subject fills the frame, no frame, no border, no text, no letters, ")
PLAN = {  # out: (art, small line, big words)
    "EP01_A": ("T01a", "December 5th:", "LOCK THE DOOR"),
    "EP01_B": ("T01b", "He works for", "A SAINT"),
    "EP02_A": ("T02a", "It is never", "FULL"),
    "EP02_B": ("T02b", "Sometimes", "IT'S YOU"),
    "EP03_A": ("T03a", "Don't ask her", "TOO MUCH"),
    "EP03_B": ("T03b", "Be kind to", "HER CAT"),
    "EP04_A": ("T04a", "If you hear hounds", "DON'T LOOK UP"),
    "EP04_B": ("T04b", "Never", "ANSWER IT"),
}
def lit_paper(w, h, cx, cy, rx, ry, dark=0.93):
    g = np.random.default_rng(3); yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    light = 1 - np.clip((r - 0.55) * 1.5, 0, dark)
    n = np.asarray(Image.fromarray((g.random((h // 8, w // 8)) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(6)), np.float32) / 255
    base = np.array(L.PAPER, np.float32)[None, None] / 255 * (0.92 + 0.12 * n[..., None])
    return base * light[..., None]
def compose(art, out, small, big):
    W, H = 1280, 720
    im = L.whiten(Image.open(os.path.join(T, art + ".jpg"))).resize((760, 760), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H), "white"); canvas.paste(im, (-10, -20))
    a = np.asarray(canvas, np.float32) / 255 * lit_paper(W, H, 360, 360, 480, 420)
    a[:, :, :] *= 1.0
    c = Image.fromarray((a.clip(0, 1) * 255).astype(np.uint8)); d = ImageDraw.Draw(c)
    cx = 1000
    fs = L.font(L.F_SC, 62); d.text((cx, 250), small, font=fs, fill=BONE, anchor="mm")
    words = big.split(); lines = [" ".join(words[:len(words) // 2]), " ".join(words[len(words) // 2:])] if len(words) > 2 else [big] if len(big) < 9 else words
    lines = [l for l in lines if l]
    size = 150 if len(lines) == 1 else 118
    fb = L.font(L.F_BOLD, size)
    while max(d.textlength(l, font=fb) for l in lines) > 520: size -= 6; fb = L.font(L.F_BOLD, size)
    y0 = 400 if len(lines) == 1 else 360
    for i, l in enumerate(lines):
        d.text((cx, y0 + i * (size + 8)), l, font=fb, fill=VERM, anchor="mm", stroke_width=3, stroke_fill=(20, 10, 6))
    L.ornament(d, cx, 175, 360, col=BONE); 
    c.save(out, quality=92)
if __name__ == "__main__":
    if sys.argv[1] == "gen":
        import gen as G
        G.STYLE = THUMB
        sc = G.load(os.path.join(T, "thumb_art.txt")); ids = sys.argv[2:] or list(sc)
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(6) as ex:
            for r in ex.map(G.run, [(k, sc[k], T) for k in ids]): print(r)
    else:
        for out, (art, small, big) in PLAN.items(): compose(art, os.path.join(T, out + ".jpg"), small, big)
