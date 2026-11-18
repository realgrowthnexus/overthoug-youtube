"""Build the Overthought branding set into brand/.

  python3 pipeline/branding.py

Outputs:
  youtube_profile_800.png      YouTube profile picture (square; YouTube shows it as a circle)
  tiktok_profile_1080.png      TikTok profile picture (tighter crop for the tiny feed avatar)
  youtube_watermark_150.png    YouTube video watermark (transparent PNG, 150x150)
  youtube_banner_2560x1440.png YouTube banner (key content inside the 1546x423 safe area)
  logo_mark_transparent.png    the scribble-head mark on transparency, for overlays
  preview_*.png                mockups of how they look in place
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, "brand") + "/"
os.makedirs(B, exist_ok=True)
LOGO = Image.open(SC + "logo_a.jpg").convert("RGB")

def lift(im):  # match the generated black to the brand charcoal
    return im.point(lambda v: int(17 + v * 238 / 255))

def glow_bg(size, strength=26):
    c = Image.new("RGB", (size, size), BG)
    g = Image.new("L", (size, size), 0)
    ImageDraw.Draw(g).ellipse((size*0.18, size*0.12, size*0.82, size*0.76), fill=strength)
    g = g.filter(ImageFilter.GaussianBlur(size * 0.12))
    return Image.composite(Image.new("RGB", (size, size), (60, 54, 30)), c, g)

def avatar(size, box):
    crop = lift(LOGO.crop(box)).resize((size, size), Image.LANCZOS)
    bg = glow_bg(size)
    # screen-blend the drawing over the glow so the lines stay bright
    from PIL import ImageChops
    return ImageChops.lighter(bg, crop)

def to_alpha(im):
    """Lines on black to lines on transparency (alpha = brightness)."""
    im = im.convert("RGB")
    a = im.convert("L").point(lambda v: 0 if v < 28 else min(255, int((v - 28) * 1.6)))
    out = im.copy(); out.putalpha(a)
    return out

def circle_preview(im, size):
    im = im.resize((size, size), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).ellipse((0, 0, size, size), fill=255)
    o = Image.new("RGBA", (size, size), (0, 0, 0, 0)); o.paste(im, (0, 0), m); return o

# 1. YouTube profile picture: scribble, head and shoulders, with breathing room
yt = avatar(800, (190, 60, 810, 680)); yt.save(B + "youtube_profile_800.png")

# 2. TikTok profile picture: tighter on scribble and head, so it reads at about 40px in the feed
tt = avatar(1080, (250, 100, 750, 600)); tt.save(B + "tiktok_profile_1080.png")

# 3. Transparent logo mark
mark = to_alpha(LOGO.crop((190, 60, 810, 680)))
mark.save(B + "logo_mark_transparent.png")

# 4. YouTube watermark 150x150: the mark on a soft dark disc so it reads over any footage
wm = Image.new("RGBA", (600, 600), (0, 0, 0, 0))
ImageDraw.Draw(wm).ellipse((10, 10, 590, 590), fill=(17, 17, 17, 190))
wm.alpha_composite(to_alpha(LOGO.crop((250, 100, 750, 600))).resize((560, 560), Image.LANCZOS), (20, 20))
wm.resize((150, 150), Image.LANCZOS).save(B + "youtube_watermark_150.png")

# 5. YouTube banner 2560x1440, safe area x 507-2053, y 508-931
W, H = 2560, 1440
ban = Image.new("RGBA", (W, H), BG + (255,))
g = Image.new("L", (W, H), 0)
ImageDraw.Draw(g).ellipse((700, 300, 1860, 1140), fill=22)
g = g.filter(ImageFilter.GaussianBlur(220))
ban = Image.composite(Image.new("RGBA", (W, H), (60, 54, 30, 255)), ban, g)
# faint doodles outside the safe area (seen on TV and full-width desktop)
def ghost(name, size, xy, op, tint=None, fill=None):
    im, m = scene(name, size, tint, fill)
    m = m.point(lambda v: int(v * op))
    ban.paste(im, xy, m)
ghost("s6b_decoy", 620, (-60, 380), 0.55, tint=[(512, 400, 62)], fill=[(512, 430)])
ghost("s1_doorway", 620, (2010, 380), 0.55)
ghost("s4d_eyeballs", 520, (60, 980), 0.30)
ghost("s3_lightbulb", 520, (1990, 980), 0.30)
ghost("s5c_eyespop", 460, (120, -40), 0.25)
ghost("s2_brainfiles", 460, (1990, -40), 0.25)
# logo figure on the left of the safe area
fig = lift(LOGO.crop((150, 40, 850, 740))).resize((470, 470), Image.LANCZOS)
fm = Image.new("L", (470, 470), 0); ImageDraw.Draw(fm).ellipse((20, 20, 450, 450), fill=255)
fm = fm.filter(ImageFilter.GaussianBlur(40))
ban.paste(fig, (560, 485), fm)
# wordmark + tagline
text_block(ban, 1040, 455, [("overthought", "ink")], 170, -2.0, 4, align="left")
text_block(ban, 1060, 700, [("why your brain ", "ink"), ("does that.", "key")], 80, -1.2, 6, align="left")
d = ImageDraw.Draw(ban)
d.text((1110, 850), "a new brain glitch, explained, every week", font=K(36), fill=DIM)
ban.convert("RGB").save(B + "youtube_banner_2560x1440.png")

# ---------- previews ----------
P = Image.new("RGB", (2400, 1500), (15, 15, 15)); pd = ImageDraw.Draw(P)
H2 = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", 32)
H3 = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 52)
# desktop channel header: YouTube shows the 2560x423 centre strip at desktop width
strip = ban.convert("RGB").crop((0, 508, 2560, 931)).resize((2240, 370), Image.LANCZOS)
P.paste(strip, (80, 80))
P.paste(circle_preview(yt, 220), (100, 490), circle_preview(yt, 220))
pd.text((360, 520), "Overthought", font=H3, fill=(240, 240, 240))
pd.text((360, 590), "@overthought  ·  Why your brain does that.", font=H2, fill=(170, 170, 170))
pd.rounded_rectangle((360, 650, 600, 710), 30, fill=(240, 240, 240)); pd.text((408, 662), "Subscribe", font=H2, fill=(15, 15, 15))
pd.text((80, 760), "YouTube desktop header (banner safe-area strip + profile)", font=H2, fill=(110, 110, 110))
# small-size checks
x = 80
for lab, im, sizes in [("YouTube", yt, (160, 88, 40)), ("TikTok", tt, (160, 88, 40))]:
    for s in sizes:
        P.paste(circle_preview(im, s), (x, 1000 - s // 2), circle_preview(im, s)); x += s + 40
    pd.text((x - sum(sizes) - 120, 1110), f"{lab} at 160/88/40px", font=H2, fill=(110, 110, 110)); x += 140
# watermark over a frame
fr = Image.open(ROOT + "/style/reference_frames/lf1.png").convert("RGBA").resize((960, 540))
w = Image.open(B + "youtube_watermark_150.png").resize((75, 75))
fr.alpha_composite(w, (960 - 75 - 20, 540 - 75 - 20))
P.paste(fr.convert("RGB").resize((720, 405)), (1600, 840))
pd.text((1600, 1260), "Watermark on a video (bottom-right)", font=H2, fill=(110, 110, 110))
P.save(B + "preview_channel.png")
print("ok")
