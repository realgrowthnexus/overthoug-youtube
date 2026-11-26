# Your Vitals ("What Happens to Your Body If…")

A faceless body-science channel. Each video puts **you** through one terrible idea (11 days awake, the Mariana Trench, a lightning strike, a month of fast food), hour by hour and organ by organ, while a live vitals monitor tracks you on screen. Every factual claim is sourced. See `LAUNCH_PLAN.md` for the strategy and `branding/CHANNEL_SETUP.md` for the copy-paste channel setup.

## Folders
- `episodes/epXX/epXX.film` holds the whole episode in one file: narration, pictures, motion, vitals, sources and fact-check. `img/` holds its generated pictures. `UPLOAD.md` and `epXX.srt` are written by `upload_kit.py`.
- `scripts/epXX_script.md` holds readable scripts with [S#] tags, sources and the fact-check list. They're generated from the film files.
- `thumbs/` holds the A/B thumbnails (`EP0X_A.jpg`, `EP0X_B.jpg`) and their art (`T0Xa/b.jpg`, prompts in `thumb_art.txt`).
- `branding/` holds the avatar, banner, watermark and CHANNEL_SETUP.md.
- `pipeline/` holds the scripts:
  - `gen.py`: Flux dev on RunPod (about $0.012 per image). The style prompt is here.
  - `vfilm.py`: `gen` makes the pictures for a film, `render` makes the finished MP4. It uses neon screen-blend sprites (power-on flicker, walk, drop, float, breathe, tremble), pulsing danger glows, particles (bubbles, marine snow, sparks, rain, Zzz) and the HUD. There's no camera shake: only slow zooms and pans, and the elements move.
  - `layers.py`: cuts small elements out of a dark scene (used with the `split` token).
  - `thumbs.py`, `brand.py`, `upload_kit.py`, `sheet.py` (contact sheet for reviewing pictures).
- `fonts/`: Anton, Oswald, JetBrains Mono, Rajdhani (all under the SIL Open Font License).
- `voices/` (not committed): download `en_GB-cori-high.onnx` and its `.json` from huggingface.co/rhasspy/piper-voices.

## Make an episode
```bash
pip install piper-tts scipy numpy pillow
python3 pipeline/vfilm.py gen    episodes/ep01/ep01.film          # pictures (skips ones that exist)
python3 pipeline/vfilm.py render episodes/ep01/ep01.film out/EP01.mp4
python3 pipeline/upload_kit.py ep01 out/EP01.times.json          # UPLOAD.md + .srt + script md
python3 pipeline/thumbs.py gen && python3 pipeline/thumbs.py compose
python3 pipeline/brand.py
```
Rendering a 9-minute episode takes about 45 minutes on 4 CPU cores. MP4s go to `out/`, which is not committed.

## Film tokens (cheat sheet)
`zoomin zoomout panl panr hold` · `glow split` · `bubbles snow sparks rain dust zzz flash alert beat` ·
`spr:NAME@x,y,scale[,enter[,idle]]` · vitals `hr= temp= o2= t= s=OK|WARN|CRIT|DEAD` (they carry forward) · `endcard`
