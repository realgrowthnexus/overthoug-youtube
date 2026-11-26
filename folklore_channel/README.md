# The Ward Book — dark folklore channel ("How to Survive ___, According to Folklore")

One legend per episode: a 2nd-person cold open, five sourced **Wards** (protective rules from the old texts), where the legend really comes from, and a verdict. The look is a woodcut on candle-lit parchment. See `LAUNCH_PLAN.md` for the strategy and `branding/CHANNEL_SETUP.md` for copy-paste channel settings.

## Folders
- `episodes/epNN/` holds `epNN.film` (the whole episode: narration, pictures, motion, sources), `img/` (generated woodcuts), `UPLOAD.md` and `epNN.srt`.
- `scripts/` holds `epNN_script.md` (readable script + sources + fact-check) and `epNN_factcheck.md`.
- `thumbs/` holds the A/B thumbnails `EPNN_A.jpg` / `EPNN_B.jpg`, their art `TNNx.jpg`, and `thumb_art.txt`.
- `branding/` holds the avatar, banner, watermark and CHANNEL_SETUP.md.
- `fonts/` holds IM Fell English (+ Italic, SC), UnifrakturMaguntia and Cinzel Bold (all SIL OFL).
- `voices/` holds the Piper voices. The .onnx files aren't in git; download them with `python3 -m piper.download_voices en_GB-alan-medium --download-dir voices`.
- `renders/` holds the MP4s. They aren't in git; re-render them with the command below.

## Pipeline (adapted from `history_channel/pipeline`)
```
pip install piper-tts scipy numpy pillow
python3 pipeline/film.py gen    episodes/ep01/ep01.film          # woodcut pictures, RunPod Flux dev, ~$0.012 each
python3 pipeline/film.py still  episodes/ep01/ep01.film k03 out.jpg 2.0   # preview one shot
python3 pipeline/film.py render episodes/ep01/ep01.film renders/EP01.mp4  # full video + renders/EP01.times.json
python3 pipeline/upload_kit.py ep01 renders/EP01.times.json      # UPLOAD.md + .srt + scripts/ep01_script.md
python3 pipeline/thumbs.py gen && python3 pipeline/thumbs.py compose
python3 pipeline/brand.py
```
What changed from the history pipeline:
- **Style:** woodcut/broadsheet prompt (`gen.py`). Pictures are drawn on white, cut into element layers (`layers.py`), animated, and only then multiplied onto a procedural parchment with a flickering candle vignette (`wardlib.finish`). The white paper look becomes aged parchment for free.
- **Motion:** new figures **bleed in like wet ink** (noise-threshold reveal) instead of popping. New idles: `sway`, `loom`, `creep`, `shiver`, plus the old breathe/bob/pulse/struggle/wag/walk. Full-width backdrops ink in and then stay still. No screen shake.
- **Particles:** snow, dust motes, embers, fog bands, bats, wind streaks, rain.
- **Cards:** `ward` (rubric card in the left margin with a red blackletter numeral, plus a "Ward N" running head until the next chapter), `quote` (printed quotation page), `title` (How to Survive / *Name*), `endcard` (next legend + end-screen box, at least 20 s).
- **Audio:** Piper `en_GB-alan-medium` (length 1.1), a light stone-room echo, a brown-noise wind drone, loudness normalised to about -14 LUFS.

## Costs so far
Roughly 110 pictures for 4 episodes, plus ~20 re-rolls, 10 thumbnail arts and ~6 tests: about **$1.80** on RunPod.
