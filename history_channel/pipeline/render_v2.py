"""Animated test v2: elements move (pop-in, breathing, sway, struggle, bob), camera only drifts. No screen shake.
Usage: python3 pipeline/render_v2.py VOICE.onnx OUT.mp4"""
import sys, os, subprocess, wave, math, tempfile, random
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_test import whiten
from layers import split
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(HERE, "..", "style", "fonts", "Kalam-Bold.ttf")
W, H, FPS, S = 1920, 1080, 24, 1080
# scene, narration, caption, camera (zoom_from, zoom_to, pan_x_px), big-element motion, small-element motion
SHOTS = [
 ("02", "You are seven years old.", "7 years old", (1.0, 1.05, 0), "pop_breathe", "bob"),
 ("01", "You're inside a chimney, in the dark. The tunnel around you is about the width of a dinner plate, and your knees are pressed up against your chin.", None, (1.0, 1.12, 0), "settle", "flicker"),
 ("01", "You can't go up. And you can't go down.", None, (1.12, 1.25, 0), "struggle", "flicker"),
 ("03", "Let's go back to how you got here.", "London, 1862", (1.15, 1.15, -90), "still", "walk"),
 ("04", "London, eighteen sixty-two. You arrive in a single rented room, shared with your parents and four siblings,", None, (1.0, 1.06, 0), "pop_breathe", "bob"),
 ("05", "and a damp patch on the wall that has more personality than your dad.", None, (1.0, 1.05, 0), "pop_breathe", "pop_breathe"),
 ("06", "Fun fact about eighteen sixty-two. A law passed twenty-two years before you were born already says nobody under twenty-one is allowed to climb a chimney.", "1840 law: no climbing under 21", (1.0, 1.06, 0), "pop_breathe", "bob"),
 ("06", "Hold on to that. It's going to be hilarious later.", None, (1.06, 1.14, 0), "breathe", "bob"),
]
def back_out(t, s=1.9):  # overshoot ease
    t = min(max(t, 0), 1) - 1; return t * t * ((s + 1) * t + s) + 1
def smooth(t): t = min(max(t, 0), 1); return t * t * (3 - 2 * t)

def place(el, motion, t, f, i, n_big, rnd):
    """Return (scale_x, scale_y, angle, dx, dy, opacity) for an element at time t (s)."""
    ph = el["phase"]; sx = sy = 1.0; ang = dx = dy = 0.0; op = 1.0
    delay = 0.12 * i
    if motion in ("pop_breathe", "pop"):
        k = back_out((t - delay) / 0.45); sx = sy = max(k, 0.001); op = 1 if t > delay else 0
    if motion in ("pop_breathe", "breathe", "settle"):
        b = math.sin(2 * math.pi * (t / 2.6 + ph))
        sy *= 1 + 0.018 * b; sx *= 1 - 0.008 * b              # squash-stretch breathing from the feet
        ang += 0.9 * math.sin(2 * math.pi * (t / 3.7 + ph))      # gentle sway around the base
    if motion == "struggle":                                      # trying to push up, sliding back
        c = (t * 1.3 + ph) % 1
        dy = -14 * math.sin(math.pi * c) ** 2; sy *= 1 + 0.025 * math.sin(math.pi * c)
    if motion == "bob":
        dy = 7 * math.sin(2 * math.pi * (t / 1.6 + ph)); ang = 3 * math.sin(2 * math.pi * (t / 2.1 + ph))
        k = back_out((t - 0.3 - 0.06 * i) / 0.35); sx = sy = max(k, 0.001)
    if motion == "flicker":                                       # panic lines twitch in place
        ang = 6 * math.sin(2 * math.pi * (t * 3 + ph)); sx = sy = 1 + 0.08 * math.sin(2 * math.pi * (t * 4 + ph))
    if motion == "walk":                                          # tiny people stroll with a step bounce
        dx = el["dir"] * 22 * t; dy = -abs(math.sin(2 * math.pi * (t * 1.8 + ph))) * 5
    return sx, sy, ang, dx, dy, op

def draw_el(canvas, el, sx, sy, ang, dx, dy, op):
    if op <= 0 or sx < 0.02: return
    img = el["img"]; w, h = img.size
    nw, nh = max(1, int(w * sx)), max(1, int(h * sy))
    im = img.resize((nw, nh), Image.BILINEAR)
    if abs(ang) > 0.05:
        big = Image.new("RGBA", (nw * 2, nh * 2), (0, 0, 0, 0)); big.paste(im, (nw // 2, nh))  # pivot at bottom centre
        im = big.rotate(ang, resample=Image.BILINEAR, center=(nw, 2 * nh - 1))
        ox, oy = el["x"] + w / 2 - nw, el["y"] + h - 2 * nh
    else:
        ox, oy = el["x"] + w / 2 - nw / 2, el["y"] + h - nh
    canvas.alpha_composite(im, (int(ox + dx), int(oy + dy)))

def main(voice, out):
    tmp = tempfile.mkdtemp(); wavs = []; durs = []
    for i, sh in enumerate(SHOTS):
        p = os.path.join(tmp, f"{i}.wav")
        subprocess.run([sys.executable, "-m", "piper", "-m", voice, "-f", p, "--length-scale", "1.05", "--sentence-silence", "0.2"],
                       input=sh[1].encode(), check=True, capture_output=True)
        with wave.open(p) as w: durs.append(w.getnframes() / w.getframerate() + 0.35); sr = w.getframerate()
        wavs.append(p)
    pad = os.path.join(tmp, "pad.wav"); lst = os.path.join(tmp, "a.txt"); audio = os.path.join(tmp, "v.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"anullsrc=r={sr}:cl=mono", "-t", "0.35", pad], check=True)
    open(lst, "w").write("".join(f"file '{p}'\nfile '{pad}'\n" for p in wavs))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", audio], check=True)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", audio, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-c:a", "aac", "-shortest", out], stdin=subprocess.PIPE)
    font = ImageFont.truetype(FONT, 72); cache = {}; rnd = random.Random(5); prev = None
    for si, ((sc, _, cap, cam, big_m, small_m), d) in enumerate(zip(SHOTS, durs)):
        if sc not in cache:
            base = whiten(Image.open(os.path.join(HERE, "scenes", sc + ".jpg"))).resize((S, S), Image.LANCZOS)
            els = split(base)
            for e in els: e["phase"] = rnd.random(); e["dir"] = rnd.choice((-1, 1))
            cache[sc] = (base, els)
        base, els = cache[sc]
        biggest = els[0]["area"] if els else 1
        bigs = [e for e in els if e["area"] > 0.06 * biggest]; smalls = [e for e in els if e["area"] <= 0.06 * biggest]
        # elements that were already on screen in the previous shot should not pop in again
        cont = prev == sc; prev = sc
        if big_m == "still":  # keep the backdrop as-is; only small elements move
            bg = base.convert("RGBA"); movers = []
            for e in smalls:
                bg.paste((255, 255, 255, 255), (e["x"], e["y"], e["x"] + e["w"], e["y"] + e["h"]), e["img"])
        else:
            bg = Image.new("RGBA", (S, S), (255, 255, 255, 255))
        n = int(d * FPS)
        for f in range(n):
            t = f / FPS; canvas = bg.copy()
            if big_m != "still":
                for i, e in enumerate(bigs):
                    m = big_m.replace("pop_", "") if cont else big_m
                    draw_el(canvas, e, *place(e, m, t, f, i, len(bigs), rnd))
            for i, e in enumerate(smalls):
                m = small_m.replace("pop_", "") if cont else small_m
                if m == "bob" and cont: m = "bob_c"
                if m == "bob_c":
                    draw_el(canvas, e, 1, 1, 3 * math.sin(2 * math.pi * (t / 2.1 + e["phase"])), 0, 7 * math.sin(2 * math.pi * (t / 1.6 + e["phase"])), 1)
                else:
                    draw_el(canvas, e, *place(e, m, t, f, i, len(smalls), rnd))
            # camera: slow drift only
            e_ = smooth(f / max(n - 1, 1)); z = cam[0] + (cam[1] - cam[0]) * e_; px = cam[2] * e_
            sz = int(S * z); img = canvas.convert("RGB").resize((sz, sz), Image.BILINEAR)
            fr = Image.new("RGB", (W, H), "white"); fr.paste(img, ((W - sz) // 2 + int(px), (H - sz) // 2))
            if cap:
                k = back_out(f / (0.4 * FPS)); dr = ImageDraw.Draw(fr)
                fs = ImageFont.truetype(FONT, max(8, int(72 * k))); dr.text((W // 2, 95), cap, font=fs, fill="black", anchor="mm")
                if f > 0.4 * FPS:  # underline draws itself on
                    u = smooth((f - 0.4 * FPS) / (0.4 * FPS)); tw = dr.textlength(cap, font=font)
                    dr.line([(W // 2 - tw / 2, 140), (W // 2 - tw / 2 + tw * u, 140 + 4 * math.sin(u * 6))], fill="black", width=5)
            ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait(); print(out, round(sum(durs), 1), "s")
if __name__ == "__main__": main(sys.argv[1], sys.argv[2])
