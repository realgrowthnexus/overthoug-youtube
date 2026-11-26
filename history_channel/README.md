# History channel ("Why It Sucks to Be Born as…")

A second channel, separate from Overthought. Each video tells a life story from human history to "you", from birth to the end, with dark humour and real sources.

> For now this folder sits inside the Overthought repo. Move it to its own repo once the channel has a name.

## Folders
- `scripts/` holds the episode scripts and a scene list for each episode. Scripts carry source tags ([S#]) and a fact-check list.
- `scenes/` holds the generated scenes: 1024² images from Flux dev on RunPod, about $0.012 each.
- `thumbs/` holds the test thumbnails.
- `frames/` holds the rendered video tests.
- `pipeline/` holds the scripts:
  - `gen.py` generates scenes from an `id | description` list. Set `SEED=` to re-roll.
  - `thumbs.py` composes thumbnails (1280×720) and frames.
  - `render_test.py` builds a test video with Piper TTS, a slow zoom, a hand-drawn wobble and captions.

## Style rules
- **Video scenes:**
  - Minimalist flat 2D webcomic style on a white background.
  - Every person has a round bald white head with dot eyes.
  - The hero wears a tattered brown shirt. His outfit changes per era.
- **Thumbnails:**
  - A detailed, gritty illustration on the left half, empty white on the right.
  - Text in Kalam Bold, two lines: a small top line and a big punch line.
  - A hand-drawn arrow points at the subject.
- **Background cleanup:** `whiten()` only whitens the backdrop that touches the image edges, so cream-coloured heads keep their colour.
- **Known gap:** Flux can't draw the boy *inside* a chimney cut-away (scenes 19 and 35). Build those two in code instead: draw the brick shaft and paste the character into it.

## Voice
- Piper TTS runs offline. The voice is `en_US-ryan-high`, from huggingface.co/rhasspy/piper-voices.
- edge-tts doesn't work here, because the proxy blocks WebSockets.
- For the real channel, a human voice or a premium TTS will sound better.
