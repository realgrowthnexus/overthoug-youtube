# New session prompt — US TikTok psychology channel (automated)

Copy everything below the line into a new Claude Code session.

---

You're helping me build and automate a **US-focused TikTok channel** about everyday psychology, drawn as stick-figure animation. It's a standalone project: it has its own ideas, scripts, tracking and pipeline. It's separate from my YouTube long-form channel, which shares the visual style and topic area but nothing else. In earlier sessions I lost all my files when the container reset, so **set up a GitHub repo for this project first and commit work as you go.**

## 1. Concept
- **Format:** short "your brain does this" explainers. Each video covers one relatable brain glitch, names a real study on screen, and ends with a payoff or fix.
- **Content split:**
  - **70% "Why you do that":** everyday glitches everyone recognises.
  - **30% "Spot the trick":** how shops, apps and people use these glitches on you, framed as protecting yourself, never as "how to manipulate people".
- **Accuracy rule:** every claim must trace to a real study or a well-established effect, cited on screen as "Researcher · Institution · Year". Flag effects that failed to replicate (for example, ego depletion and power posing) instead of presenting them as fact. Correct famous myths, such as the 38-witnesses story in the Kitty Genovese case.
- **Audience:** US, English, ages 16–34. Use US references: dollars, US stores, US school and work life.
- **Channel name:** not chosen yet. Shortlist: Overthought (current favourite), Why You Did That, Mind Glitch, Brainfold, Inner Static, Skull Notes, Little Brain, The Mind Room, Thinkhole, Neuronly. Help me pick one and remind me to check handle availability on TikTok, Instagram and YouTube.

## 2. Visual style (already approved, keep it consistent)
- **Background:** near-black charcoal `#111111`, not pure `#000000`, so frames don't melt into dark-mode UI or band under compression. Add a subtle centre glow or vignette.
- **Character:** a classic stick figure in thin white hand-drawn lines: circle head, single-line body, line arms and legs. Use **one fixed character design** across all videos. Open decision: plain white head, or a yellow head as the mascot.
- **Accent:** electric yellow `#FFE000`, used only on the "glitch" element: a question mark, lightbulb, decoy price tag, key number or keyword.
- **Captions:**
  - Font: Inter ExtraBold, white with a black stroke.
  - Exactly **one yellow keyword** per caption.
  - Hook text at the top, punchline at the bottom.
  - Keep captions out of TikTok's UI zones: right-side buttons, bottom caption and username area, top tabs. Safe area is about the central 1080×1420 of a 1080×1920 frame.
- **Citation tag:** a small yellow rounded outline box with yellow text, for example `Radvansky · Univ. of Notre Dame · 2011`.
- **Mood:** late-night inner voice, minimal and mostly empty space. A quick yellow or white flash marks the payoff beat.
- **Never** let the image model draw text. All text is added in code (PIL or ffmpeg) so it's spelled right and looks the same every time.

### Image generation (RunPod)
- **Endpoint:** RunPod serverless Flux dev, `POST https://api.runpod.ai/v2/black-forest-labs-flux-1-dev/runsync`. The API key is saved as a network secret on my Default cloud environment and the proxy injects it. If calls return 401, ask me for the key with the credential tool.
- **Request body:** `{"input":{"prompt":...,"num_inference_steps":28,"guidance":3.5,"seed":N}}`
- **Response:** the image URL is in `output.result`.
- **Size and cost:** output is always 1024×1024, whatever size you request. About $0.012 per image (the schnell endpoint is about $0.003, for drafts).
- **Prompt prefix that works:**
  `classic stick figure made of single thin white lines: circle head, one straight line body, two line arms, two line legs, on pure black background, flat minimal hand-drawn vector, glowing electric yellow accent, no shading, no text, no letters, ` + scene description
- **Prompt rules:** say "the stick figure is pure white lines" explicitly, or the model sometimes turns the figure yellow. Keep seeds fixed per character for consistency. Consider a character reference or LoRA approach if drift stays a problem.
- **Composing a 9:16 frame:**
  - Upscale the square scene to 1080×1080 and paste it at y≈420 on a 1080×1920 canvas.
  - Blend the edges with a Gaussian-blurred mask, and fill the canvas with the scene's corner colour so there are no visible seams.
  - Captions go above and below the scene.

### Animation (to build)
These are still scenes turned into motion:
- lines drawing on
- the accent element popping or glowing
- slow push-in or Ken Burns movement
- word-by-word captions synced to the voiceover
- the loop line at the end leading back into the hook

Tools: ffmpeg, Python, optionally Remotion or MoviePy. Propose the simplest pipeline that looks good.

## 3. TikTok-specific format
- **Length:**
  - Most videos: 30–60 seconds.
  - Some 61–75 second versions: videos over 1 minute qualify for the Creator Rewards Program, which needs a US account aged 18+, 10k followers and 100k views in the last 30 days. Verify the current rules.
- **Opening:** the first 1 second must show the payoff image plus a hook line. No intros, no logo stings.
- **Voiceover:** natural US English text-to-speech, or my own voice. Pick a TTS engine and confirm the commercial-use licence. Keep one consistent voice.
- **Ending:** a loop line that leads back to the first line.
- **On-screen text** plus a caption with 3–5 hashtags (mix niche and broad, for example #psychology #brainfacts #didyouknow).
- **Sound:** trending sounds can't be added through the API. Plan a low-volume original music bed, and note which videos I should repost manually with a trending sound.
- **AI disclosure:** TikTok requires the AI-generated content label for realistic AI media. Check whether it applies to stylised stick-figure art and default to labelling.

## 4. Idea bank (starting 30, build to 100+)
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

**Three approved scripts to adapt:**
- **Doorway effect.** Radvansky, Notre Dame, 2011: people forgot more after walking through a doorway than after walking the same distance in one room. Fix: walk back through the door. Loop line: "So next time you're standing there wondering why you came in…"
- **Spotlight effect.** Gilovich et al., Cornell, 2000: students in an embarrassing T-shirt guessed about 50% of the room noticed; about 25% did. Loop line: "So that thing you did yesterday that you're still thinking about…"
- **Decoy effect.** Dan Ariely's Economist subscription example: Web $59, Print $125, Print + Web $125. 84% chose the bundle with the decoy present; without it, most chose web-only. Loop line: "Now go back and look at that menu again…"

## 5. Tracking
Build a tracker. I'm open to a database, a sheet or a dashboard; suggest one. For each video it records:
- **Plan:** idea, angle (why or trick), hook text, study source, script version
- **Production:** status (idea → script → visuals → voice → edit → scheduled → posted), post date and time
- **Results:** views, average watch time, % watched full, likes, comments, shares, saves, follows gained

Weekly review:
- Double down on topics and hook styles that beat the channel median for completion and shares.
- Retire what doesn't work.
- Test one variable at a time: hook wording, length, mascot head colour, music.

Getting stats in: the TikTok Display or Research APIs where available, otherwise a CSV export or manual entry.

## 6. Automation goal
I want Claude to run as much of this as possible:
1. Generate and rank ideas.
2. Write scripts with sources.
3. Generate scenes on RunPod.
4. Produce the TTS voiceover.
5. Animate and edit to MP4 (1080×1920, H.264, 30fps).
6. Write captions and hashtags.
7. Queue for posting.
8. Pull stats and update the tracker.
9. Write a weekly report.

**Guardrails:**
- **Posting:** TikTok's Content Posting API needs a registered developer app, and unaudited apps can only post privately. Plan the app registration and audit, or a draft-upload flow where I press publish. Don't use unofficial auto-posting bots or browser automation that breaks TikTok's terms; the account is the asset.
- **Quality:** every video needs a real hook, story and source. Avoid mass-produced, repetitive content, because both TikTok and YouTube suppress or demonetize it.
- **Approval:** keep a human checkpoint before anything goes public, at least for the first month.

## 7. First tasks this session
1. Set up the GitHub repo and folder structure: ideas, scripts, assets, renders, tracker, pipeline.
2. Help me pick the name, then make the profile picture, banner or cover, and bio in the approved style.
3. Lock the character design: generate 4 variants and let me choose.
4. Build the pipeline end to end for script #1 (doorway effect) and show me the finished MP4.
5. Propose the tracker and a 30-day posting calendar (aim for 1–2 posts a day), then show me the plan for the next 10 videos.

Ask me before anything that posts publicly, spends more than a few dollars, or creates accounts.
