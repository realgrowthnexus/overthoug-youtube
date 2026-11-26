"""Cut the hook of a rendered episode into a vertical Short (1080x1920): the centre square of the video on a
candle-lit parchment card, with the title on top and a call to action below.
Usage: python3 pipeline/short.py renders/EP01.mp4 "Krampus" OUT.mp4 TITLE_SHOT_ID   (e.g. k07; the cut ends 4 s into the title plate)"""
import os, sys, json, subprocess
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wardlib as L
from thumbs import lit_paper
def card(name, out):
    W, H = 1080, 1920; c = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(c)
    d.text((W // 2, 250), "How to Survive", font=L.font(L.F_SC, 84), fill=L.INK, anchor="mm")
    d.text((W // 2, 390), name, font=L.font(L.F_BLACK, 150 if len(name) < 10 else 120), fill=L.OCHRE, anchor="mm")
    L.ornament(d, W // 2, 1560, 520)
    d.text((W // 2, 1650), "Five wards. Full video on the channel.", font=L.font(L.F_ITAL, 54), fill=L.INK, anchor="mm")
    d.text((W // 2, 1740), "The Ward Book", font=L.font(L.F_BLACK, 80), fill=L.OCHRE, anchor="mm")
    a = np.asarray(c, np.float32) / 255 * lit_paper(W, H, W / 2, H / 2, 900, 1250, dark=0.9)
    Image.fromarray((a.clip(0, 1) * 255).astype(np.uint8)).save(out)
if __name__ == "__main__":
    src, name, out = sys.argv[1:4]
    tj = os.path.splitext(src)[0] + ".times.json"
    times = json.load(open(tj)); title = next(t["start"] for t in times if t["id"] == sys.argv[4])
    dur = min(59.0, title + 4)
    bg = os.path.splitext(out)[0] + "_card.png"; card(name, bg)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", bg, "-t", f"{dur}", "-i", src, "-filter_complex",
                    "[1:v]crop=1080:1080:420:0[v];[0:v][v]overlay=0:450:shortest=1,format=yuv420p[o]",
                    "-map", "[o]", "-map", "1:a", "-t", f"{dur}", "-c:v", "libx264", "-crf", "20", "-c:a", "aac", "-b:a", "160k", out], check=True)
    os.remove(bg); print(out, dur)
