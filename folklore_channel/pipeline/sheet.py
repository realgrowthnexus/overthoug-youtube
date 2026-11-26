"""Contact sheet of an episode's pictures: python3 pipeline/sheet.py episodes/ep01/img OUT.jpg"""
import sys, os
from PIL import Image, ImageDraw
d = sys.argv[1]; fs = sorted(f for f in os.listdir(d) if f.endswith(".jpg")); n = 6; t = 256
c = Image.new("RGB", (n * t, ((len(fs) + n - 1) // n) * (t + 20)), "white"); dr = ImageDraw.Draw(c)
for i, f in enumerate(fs):
    x, y = (i % n) * t, (i // n) * (t + 20); c.paste(Image.open(os.path.join(d, f)).resize((t, t)), (x, y + 20)); dr.text((x + 4, y + 4), f, fill="black")
c.save(sys.argv[2], quality=85)
