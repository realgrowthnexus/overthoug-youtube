# EP03 upload kit — Your Vitals

**Publish:** Wednesday 16 December 2026, 16:00 UTC (11:00 AM New York, 4:00 PM London, 9:00 PM Pakistan). Upload as Private 24 h before, then Schedule.

## Title
What Happens to Your Body If You Get Struck by Lightning

## Thumbnails (YouTube "Test & Compare" with both)
- `thumbs/EP03_A.jpg`
- `thumbs/EP03_B.jpg`

## Description
```
300 million volts, and 9 in 10 people survive. That's not the good news you think it is.

A direct lightning strike, second by second: flashover across your skin, a heart that stops and restarts by itself, breathing that doesn't, temporary paralysis, fern-shaped 'lightning tattoos', and the invisible brain injury many survivors live with. Plus Roy Sullivan, the park ranger struck seven times.

Every factual claim in this video comes from a source listed below. The jokes are ours. This is entertainment and education, not medical advice.

⏱️ Chapters
0:00 Hook
0:37 T-Minus 30 Minutes
1:20 How It Finds You
2:04 0.000 Seconds: The Strike
3:25 +1 Minute: The Aftermath
4:16 +1 Week: The Invisible Injury
5:19 The Man Struck Seven Times
6:24 How To Not Be Roy
7:18 Outro

📚 Sources
[S1] NOAA National Weather Service, "Lightning: power": a typical flash is ~300 million volts and ~30,000 amps; household current 120 V / 15 A. https://www.weather.gov/safety/lightning-power
[S2] NOAA National Weather Service, "How hot is lightning?": air heated to ~50,000 °F, five times hotter than the surface of the Sun. https://www.weather.gov/safety/lightning-temperature
[S3] NOAA National Weather Service, "How dangerous is lightning?": ~10% of people struck are killed, ~90% left with various degrees of disability; average 43 US deaths/yr (1989–2018), 27/yr (2009–2018); odds 1 in 1,222,000 per year, 1 in 15,300 in a lifetime; ~10 people affected for every 1 struck; cardiac arrest at the time of injury. https://www.weather.gov/safety/lightning-odds
[S4] NOAA National Weather Service, "How lightning strikes people": direct strike (flashover over the skin surface, portion through cardiovascular/nervous systems), side flash, ground current (most deaths and injuries), conduction (most indoor casualties), streamers. https://www.weather.gov/safety/lightning-struck
[S5] NOAA National Weather Service, "Lightning myths": strikes >3 miles from the storm, bolts from the blue 10–15 miles; strikes the same place repeatedly (Empire State Building ~23 times a year); under a tree is the second leading cause of casualties; crouching doesn't make you safer; lying flat increases ground-current risk; the body does not store electricity. https://www.weather.gov/safety/lightning-myths
[S6] NOAA National Weather Service, "Medical aspects of lightning" (Dr Mary Ann Cooper): primarily a nervous-system injury; serious burns seldom occur; headaches, nausea, memory and learning problems, sleep changes; scans often "normal"; social isolation. https://www.weather.gov/safety/lightning-medical
[S7] Wikipedia, "Lightning injury": ~10% lethal; initial asystole and respiratory arrest, asystole may resolve spontaneously while respiratory arrest is more prolonged; ~75% of survivors have ongoing problems (e.g., cataracts, hearing loss); keraunoparalysis (pulselessness, pallor/cyanosis, limb paralysis) usually resolves within hours; ruptured eardrums; cataracts may develop more than a year later. https://en.wikipedia.org/wiki/Lightning_injury
[S8] NOAA National Weather Service, "How lightning strikes people" (call 911, start CPR, use an AED). https://www.weather.gov/safety/lightning-struck
[S9] Wikipedia, "Lichtenberg figure": fern-like patterns on the skin of lightning victims (keraunographic markings) that typically disappear in about 24 hours. https://en.wikipedia.org/wiki/Lichtenberg_figure
[S10] Wikipedia, "Roy Sullivan": Shenandoah National Park ranger; struck seven times 1942–1977; Guinness record; 1942 fire lookout tower without a lightning rod, eyebrows/eyelashes burned off and hair set alight; strikes in his front yard (1970) and in a ranger station (1972); believed clouds followed him; carried a can of water; avoided by people. https://en.wikipedia.org/wiki/Roy_Sullivan
[S11] NOAA National Weather Service, "Understanding lightning" ("if you hear thunder ... you are already in danger") and lightning safety pages (safe shelter = substantial building or hard-topped metal vehicle). https://www.weather.gov/safety/lightning-science-overview
[S12] Ritenour AE, Morton MJ, McManus JG, Barillo DJ, Cancio LC. Lightning injury: a review. Burns 2008;34(5):585–594 (background review used for cross-checking). https://doi.org/10.1016/j.burns.2007.11.006

🩺 New patient every Wednesday. Subscribe so you don't flatline.

#WhatHappensToYourBody #science #YourVitals
```

## Tags
what happens to your body if, struck by lightning, lightning strike, lightning survivor, roy sullivan, lichtenberg figure, lightning safety, human body, body science, your vitals, science explained

## Settings
- Category: **Science & Technology**. Language: English. Captions: upload `episodes/ep03/ep03.srt` (English).
- Audience: **No, it's not made for kids**.
- **Altered or synthetic content: Yes.** The narration voice and the pictures are AI-generated. YouTube asks for this label; it does not affect reach.
- Paid promotion: No. Comments: On (hold potentially inappropriate for review).
- End screen (last 20 s): right box = "Best for viewer" video, circle bottom = Subscribe. The left side of the frame is kept clear for the elements.
- Playlist: "What Happens to Your Body If…".
- Video file: render with `python3 pipeline/vfilm.py render episodes/ep03/ep03.film out/EP03.mp4` (MP4s are not committed).

## Pinned comment
Have you (or someone you know) ever been close to a lightning strike? 👇

## Shorts (cut from this video, 9:16, 30–50 s, posted Fri and Sun after the long video; link the long video as "Related video")
1. Lightning gives you a tattoo… then takes it back. #lightning #science
2. This man was struck by lightning 7 times. #science #weird

### Cut points (vertical 1080×1920, made from the rendered episode)
- Short 1: start 3:25.9, 50.5 s, on-screen title "LIGHTNING GIVES YOU A TATTOO". Make it with `python3 pipeline/shorts.py out/EP03.mp4 205.92 50.5 "LIGHTNING GIVES YOU A TATTOO" out/EP03_short1.mp4`
- Short 2: start 5:19.7, 59 s, on-screen title "STRUCK BY LIGHTNING 7 TIMES". Make it with `python3 pipeline/shorts.py out/EP03.mp4 319.71 59 "STRUCK BY LIGHTNING 7 TIMES" out/EP03_short2.mp4`
