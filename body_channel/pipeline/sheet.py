"""Contact sheet of an episode's pictures: python3 pipeline/sheet.py episodes/ep01/img OUT.jpg"""
import sys, os
from PIL import Image, ImageDraw
d = sys.argv[1]; fs = sorted(f for f in os.listdir(d) if f.endswith(".jpg"))
n = 8; t = 240; rows = (len(fs) + n - 1) // n
c = Image.new("RGB", (n * t, rows * (t + 20)), "black"); dr = ImageDraw.Draw(c)
for i, f in enumerate(fs):
    x, y = (i % n) * t, (i // n) * (t + 20)
    c.paste(Image.open(os.path.join(d, f)).convert("RGB").resize((t, t)), (x, y)); dr.text((x + 4, y + t + 4), f[:-4], fill="white")
c.save(sys.argv[2], quality=85)
