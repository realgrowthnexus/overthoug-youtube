"""Cut a vertical Short (1080x1920) from a rendered episode: the 1080x1080 stage in the middle, a title on top,
the vitals panels stacked underneath. Usage:
    python3 pipeline/shorts.py out/EP01.mp4 START_SECONDS DURATION "TOP TITLE" out/EP01_short1.mp4"""
import sys, os, subprocess
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F_BIG = os.path.join(ROOT, "fonts", "Anton-Regular.ttf")
src, start, dur, title, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5]
ov = Image.new("RGBA", (1080, 1920), (3, 5, 10, 255)); d = ImageDraw.Draw(ov)
d.rectangle([0, 300, 1080, 1380], fill=(0, 0, 0, 0))                     # hole for the stage
s = 110
while s > 40 and d.textlength(title, font=ImageFont.truetype(F_BIG, s)) > 1000: s -= 4
d.text((540, 140), title, font=ImageFont.truetype(F_BIG, s), fill=(255, 122, 26), anchor="mm")
d.text((540, 250), "YOUR VITALS · full video linked below", font=ImageFont.truetype(F_BIG, 40), fill=(70, 225, 255), anchor="mm")
png = out + ".overlay.png"; ov.save(png)
# stage: x 420..1500 of the 1920 frame; side panels: left 28..392, right 1528..1892 (rows 40..760 hold the numbers)
fc = ("[0:v]split=3[a][b][c];[a]crop=1080:1080:420:0[st];[b]crop=364:400:28:40,scale=480:-1[l];[c]crop=364:400:1528:40,scale=480:-1[r];"
      "color=c=0x03050A:s=1080x1920:d=%.2f[bg];[bg][st]overlay=0:300[v1];[v1][1:v]overlay=0:0[v2];[v2][l]overlay=40:1390:shortest=1[v3];[v3][r]overlay=560:1390:shortest=1[v4];"
      "[v4]crop=1080:1920:0:0[v]" % dur)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(start), "-t", str(dur), "-i", src, "-i", png, "-filter_complex", fc,
                "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-c:a", "aac", out], check=True)
os.remove(png); print(out)
