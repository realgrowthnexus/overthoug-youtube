# overthought

A YouTube channel (long-form and Shorts) about everyday brain glitches, drawn as stick-figure animation and backed by real studies.

## Style kit (approved)
| Element | Spec |
|---|---|
| Background | `#111111` charcoal with a soft centre glow. Never pure black |
| Character | Thin white hand-drawn stick figure. **Never yellow** |
| Accent | `#FFD60A` yellow, only on the glitch element, added in code |
| Body text | Kalam Bold, warm off-white `#F6F1E6`, soft blurred shadow, tilted 1–2° |
| Keyword | Caveat Brush, yellow, about 1.2× size, wobbly hand-drawn underline. One per frame |
| Source | Yellow margin note with a hand-drawn arrow: `→ Name · Institution · Year` |
| Logo / avatar | Yellow tangled scribble cloud above the figure's head (`scenes/s7_thumb.jpg`) |
| Corner tag | Lowercase handwritten "overthought" plus a small yellow scribble |
| Long-form layout | Text on the left, scene on the right, narration subtitle at the bottom |
| Shorts layout | Hook at the top, scene in the middle, punchline and source at the bottom (1080×1920) |
| Thumbnail | 3–4 big handwritten words, one yellow highlighted word, one strong image |

Reference frames: `style/reference_frames/`

## Pipeline
- `pipeline/gen_scenes.py`: generates a scene on RunPod with Flux dev. The key is injected by the cloud environment proxy.
- `pipeline/style.py`: composes frames (`short()`, `longform()`, `text_block()`, `margin_note()`, `bug()`), adds yellow tint and fill, and blends edges.
- `pipeline/build_frames.py`: renders the reference frames into `renders/`.

```
python3 pipeline/gen_scenes.py s8_gorilla "stick figure gorilla walking through a group of stick figures passing a ball"
python3 pipeline/build_frames.py
```

## Scripts
- `scripts/lf01_your_brain_lies.md`: long-form video 1, about 10 minutes, 7 glitches.

## Fonts
Kalam and Caveat Brush are from Google Fonts under the SIL Open Font License, so commercial use is allowed.

## Brand assets (`brand/`)
| File | Use | Upload where |
|---|---|---|
| `youtube_banner_2560x1440.png` | Channel banner. Key content sits in the 1546×423 safe area | YouTube Studio → Customization → Branding → Banner |
| `youtube_profile_800.png` | Profile picture | YouTube Studio → Customization → Branding → Picture |
| `youtube_watermark_150.png` | Video watermark, transparent. Set to "entire video" | YouTube Studio → Customization → Branding → Video watermark |
| `tiktok_profile_1080.png` | TikTok profile picture, tighter crop so it reads in the feed | TikTok → Edit profile → Change photo |
| `logo_mark_transparent.png` | The scribble-head mark on transparency, for intros, end screens and overlays | — |
| `preview_channel.png` | Mockup of the channel header, small-size checks and the watermark | — |

Rebuild with `python3 pipeline/branding.py`. The source drawing is `scenes/logo_a.jpg`.
