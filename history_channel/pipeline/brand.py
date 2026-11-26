"""Channel branding for Ink and Humanity: avatar (800x800), banner (2560x1440, text inside the 1546x423 safe area),
watermark (150x150). Usage: python3 pipeline/brand.py"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from layers import split
from render_test import whiten
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(ROOT, "..", "style", "fonts", "Kalam-Bold.ttf")
RED, INK, PAPER = (178, 34, 34), (20, 20, 20), (250, 247, 240)
def cut(path, i=0): return split(whiten(Image.open(os.path.join(ROOT, path))).resize((1024, 1024)))[i]

def avatar():
    b = cut("branding/B_sweep.jpg")["img"]; bb = b.getbbox(); b = b.crop(bb)
    head = b.crop((0, 0, b.width, int(b.height * 0.55)))          # head + shoulders
    A = 800; c = Image.new("RGBA", (A, A), RED + (255,))
    d = ImageDraw.Draw(c); d.ellipse([60, 60, A - 60, A - 60], fill=PAPER)
    s = 500 / head.height; head = head.resize((int(head.width * s), int(head.height * s)), Image.LANCZOS)
    mask = Image.new("L", (A, A), 0); ImageDraw.Draw(mask).ellipse([60, 60, A - 60, A - 60], fill=255)
    layer = Image.new("RGBA", (A, A)); layer.alpha_composite(head, ((A - head.width) // 2 + 30, A - head.height - 60))
    layer.putalpha(Image.composite(layer.getchannel("A"), Image.new("L", (A, A), 0), mask))
    c.alpha_composite(layer); c.convert("RGB").save(os.path.join(ROOT, "branding", "avatar_800.png"))
    c.convert("RGB").resize((150, 150), Image.LANCZOS).save(os.path.join(ROOT, "branding", "watermark_150.png"))

def banner(figs):
    Wb, Hb = 2560, 1440; c = Image.new("RGBA", (Wb, Hb), PAPER + (255,)); d = ImageDraw.Draw(c)
    sx0, sy0, sw, sh = (Wb - 1546) // 2, (Hb - 423) // 2, 1546, 423       # safe area (shows on every device)
    d.rectangle([0, sy0 + sh - 10, Wb, sy0 + sh], fill=INK)                 # hand-drawn ground line
    title = ImageFont.truetype(F, 98); small = ImageFont.truetype(F, 46)
    d.text((Wb // 2, sy0 + 150), "Ink and Humanity", font=title, fill=INK, anchor="mm")
    d.text((Wb // 2, sy0 + 265), "A new terrible life every Friday.", font=small, fill=RED, anchor="mm")
    # characters stand on the line, two each side of the title
    xs = [sx0 + 80, sx0 + 245, sx0 + sw - 245, sx0 + sw - 80]
    for x, f in zip(xs, figs):
        b = cut(*f)["img"]; b = b.crop(b.getbbox()); s = 300 / b.height
        b = b.resize((int(b.width * s), 300), Image.LANCZOS); c.alpha_composite(b, (int(x - b.width / 2), sy0 + sh - 10 - 300 + 6))
    c.convert("RGB").save(os.path.join(ROOT, "branding", "banner_2560x1440.png"))

if __name__ == "__main__":
    avatar()
    if len(sys.argv) > 1: banner([(p, 0) for p in sys.argv[1:5]])
