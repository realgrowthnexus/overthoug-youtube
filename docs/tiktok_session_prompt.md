# New session prompt: Overthought on TikTok (US, automated)

Copy everything below the line into a new Claude Code session.

---

You're helping me build and automate a **US-focused TikTok channel called "Overthought"**: everyday psychology explained with stick-figure animation. My YouTube channel uses the same brand, and its style kit, logo and pipeline already exist in the GitHub repo **`realgrowthnexus/overthoug-youtube`**. The TikTok project keeps its **own ideas, scripts, tracking and automation**.

## 0. Setup first
1. **Attach the brand repo** `realgrowthnexus/overthoug-youtube` and read its `README.md`.
   - Reuse `brand/`, `style/`, `pipeline/style.py`, `pipeline/gen_scenes.py`, `style/fonts/` and `scenes/`. Copy them; don't fork the style.
2. **Store all TikTok work in its own repo** so nothing is lost when the container resets. Ask me for the repo name (I'll create it on GitHub), attach it, and commit as you go.
3. **RunPod image generation:** the API key is saved as a network secret on my Default cloud environment, and the proxy injects it.
   - If you get a 401, ask me for the key with the credential tool.
   - Never ask me to paste it into chat.

## 1. Concept
- **Format:** short "your brain does this" explainers. Each video covers one relatable brain glitch, names a real study on screen, and ends with a payoff or fix.
- **Content split:**
  - **70% "Why you do that":** everyday glitches everyone recognises.
  - **30% "Spot the trick":** how shops, apps and people use these glitches on you, always framed as protecting yourself, never as "how to manipulate people".
- **Accuracy is the brand.** Every claim must trace to a real study, shown on screen as `→ Researcher · Institution · Year`.
  - Flag effects that failed to replicate (for example, ego depletion and power posing) instead of presenting them as fact.
  - Correct famous myths, such as the "38 witnesses" in the Kitty Genovese case.
  - Never round a stat into something false. "About 25% noticed" must not become "nobody noticed".
- **Audience:** US, English, ages 16–34. Use US references: dollars, US stores, US school and work life.
- **Handle:** @overthought if it's free. I'll confirm what I got.

## 2. Approved visual style (already locked, don't redesign)
| Element | Spec |
|---|---|
| Background | Charcoal `#111111` with a soft centre glow. Never pure black. Lift generated blacks to `#111` so there are no seams |
| Character | Thin white hand-drawn stick figure, **never yellow** |
| Accent | Yellow `#FFD60A`, only on the glitch element (a question mark, lightbulb, decoy tag, key number). **Add yellow in code**, not in the image prompt |
| Body text | **Kalam Bold**, warm off-white `#F6F1E6`, soft blurred shadow (no hard outline), lines tilted 1–2° |
| Keyword | **Caveat Brush** in yellow, about 1.2× size, with a wobbly hand-drawn yellow underline. **One keyword per frame** |
| Source | Yellow margin note with a hand-drawn arrow: `→ Gilovich · Cornell · 2000` |
| Logo | Stick figure with a tangled yellow scribble bursting from its head (`scenes/logo_a.jpg`) |
| Corner tag | Lowercase handwritten "overthought" plus a small yellow scribble |
| 9:16 layout | Hook at the top, scene in the middle (1080×1080 at y≈430), punchline and source at the bottom |
| Mood | Late-night inner voice. Minimal, mostly empty space, quick yellow or white flash on the payoff |

**Ready-made assets** in the brand repo:
- `brand/tiktok_profile_1080.png`: the TikTok profile picture.
- `brand/logo_mark_transparent.png`: the logo on a transparent background.
- `style/reference_frames/sh1–sh4.png`: approved 9:16 frames to match.

**TikTok safe zones:** keep all text inside roughly the central 1080×1420 of the 1080×1920 frame, clear of the right-side buttons, the bottom caption and username area, and the top tabs. Adjust `short()` if needed.

### Image generation lessons (RunPod Flux dev)
- **Run it:** `python3 pipeline/gen_scenes.py NAME "scene description" [--seed N] [--yellow]`. It costs about $0.012 per image.
- **Size:** output is always 1024×1024, whatever size you request.
- **Colour:** the default prompt is monochrome white. If you ask the image model for yellow, it often turns the character yellow too. Use `--yellow` only for the scribble-cloud type of element, and add other accents with `style.scene(..., tint=[(x,y,r)], fill=[(x,y)])`.
- **Never let the model draw text.** All text goes on in code, so it's spelled right and looks the same every time.
- **Consistency:** keep seeds and prompt wording stable. Regenerate when the figure drifts.

## 3. TikTok-specific format
- **Length:** mostly 30–60 seconds. Make some versions over 1 minute, because longer videos qualify for the Creator Rewards Program, which needs a US account aged 18+, 10k followers and 100k views in the last 30 days. Verify the current rules.
- **Opening:** the payoff image plus the hook line in the first second. No intros.
- **Ending:** a loop line that leads back to the opening line.
- **Voiceover:** a calm, warm, slightly amused US English voice, like a smart friend at 2 a.m. Choose a text-to-speech engine with a commercial licence and keep one consistent voice.
- **Caption:** a short hook plus 3–5 hashtags, mixing niche and broad (for example #psychology #brainfacts #didyouknow).
- **Sound:** trending sounds can't be added through the API. Use a low original music bed, and flag videos worth reposting manually with a trending sound.
- **AI label:** check whether TikTok's AI-generated content label applies to stylised art. Default to using it.

## 4. Idea bank (start with these 30, build to 100+)
**Why you do that**
1. doorway effect
2. cocktail party effect
3. hypnic jerk
4. earworms
5. 2 a.m. embarrassment
6. can't tickle yourself
7. time speeds up with age
8. spotlight effect
9. frequency illusion
10. pareidolia
11. phantom vibrations
12. procrastinating on the important task
13. shower arguments
14. forgetting dreams
15. strangers telling you secrets
16. chameleon effect
17. peak-end rule
18. idle waiting feels longer
19. loss aversion
20. sunk cost

**Spot the trick**
21. decoy effect
22. $9.99 pricing
23. Ben Franklin effect
24. confidence heuristic
25. foot in the door
26. silence makes people talk
27. "FREE"
28. "only 2 left"
29. red notification dots
30. bystander effect, plus the Genovese myth

**Also adapt:** the 7 glitches in `scripts/lf01_your_brain_lies.md` in the brand repo. That's the YouTube long-form script, with sources and a fact-check list.

## 5. Tracking
Build a tracker and propose the format. For each video it records:
- **Plan:** idea, angle (why or trick), hook text, source, script version
- **Production:** status (idea → script → visuals → voice → edit → scheduled → posted), post date and time
- **Results:** views, average watch time, % watched full, likes, comments, shares, saves, follows gained

**Weekly review:**
- Double down on topics and hook styles that beat the channel median for completion and shares.
- Retire what doesn't work.
- Test one variable at a time: hook wording, length, music.

## 6. Automation goal
I want you to run as much of this as possible:
1. Rank ideas.
2. Write scripts with sources.
3. Generate scenes on RunPod.
4. Produce the voiceover.
5. Animate and edit to MP4 (1080×1920, H.264, 30fps), with:
   - lines drawing on
   - the accent element popping
   - a slow push-in
   - word-by-word captions synced to the voice
6. Write the caption and hashtags.
7. Queue for posting.
8. Pull stats and update the tracker.
9. Write a weekly report.

**Guardrails:**
- **Posting:** use TikTok's official Content Posting API through a registered developer app. Until TikTok approves the app, it can only post privately, so use a draft-upload flow where I press publish. No unofficial bots or browser automation; the account is the asset.
- **Quality:** every video needs a real hook, story and source. No mass-produced, repetitive content.
- **Approval:** I approve every video before it goes public, at least for the first month.
- **Ask first** before anything that posts publicly, spends more than a few dollars, or creates accounts.

## 7. First tasks this session
1. Attach the brand repo, set up the TikTok repo and folder structure, and copy the shared style kit.
2. Write the TikTok bio, about 80 characters. Suggested start: "why your brain does that. real studies, tiny stick figures."
3. Adapt the frame composer to TikTok's safe zones.
4. Build the pipeline end to end for the doorway-effect video and show me the finished MP4.
5. Propose the tracker and a 30-day posting calendar (1–2 posts a day), then show me the plan for the next 10 videos.
