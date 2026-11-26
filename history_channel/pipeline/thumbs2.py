"""Episode thumbnails (1280x720): gritty detailed art on the left, 2-3 handwritten words + arrow on the right.
Usage: python3 pipeline/thumbs2.py gen   (art, ~$0.012 each)   |   python3 pipeline/thumbs2.py compose"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); T = os.path.join(ROOT, "thumbs")
THUMB = ("detailed digital illustration, bold black ink outlines, cel shading, muted gritty colors, dramatic close-up, "
         "isolated on plain pure white background, subject fills the left 55 percent of the frame, right side completely empty white, no text, no letters, ")
# file: (art, small line, big words, arrow target, x shift)
PLAN = {
    "EP01_A": ("T01a", "7 years old", "Stuck Inside", (640, 260), -20),
    "EP01_B": ("T01b", "Illegal since", "1840", (600, 300), -60),
    "EP02_A": ("T02a", "Everyone", "Hates You", (560, 250), -160),
    "EP02_B": ("T02b", "The killer was", "Secret Doctor", (600, 420), -160),
    "EP03_A": ("T03a", "The mask", "Did Nothing", (560, 330), -100),
    "EP03_B": ("T03b", "Paid to", "Walk In", (620, 300), -80),
    "EP04_A": ("T04a", "Freedom was", "Even Worse", (560, 330), -110),
    "EP04_B": ("T04b", "Your life:", "One Thumb", (620, 200), -100),
}
if __name__ == "__main__":
    if sys.argv[1] == "gen":
        import gen as G
        G.STYLE = THUMB; G.HERO = ""
        sc = G.load(os.path.join(T, "thumb_art.txt"))
        for k in (sys.argv[2:] or sc): print(G.run((k, sc[k], T)))
    else:
        import thumbs as TH
        for out, (art, small, big, arr, dx) in PLAN.items():
            TH.thumb(os.path.join(T, art + ".jpg"), os.path.join(T, out + ".jpg"), small, big, arr, dx=dx)
