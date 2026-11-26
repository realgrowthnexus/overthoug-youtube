# The Ward Book — launch plan (month 1: "Monsters of the Long Night")

## The channel (locked)
| | |
|---|---|
| **Name** | The Ward Book |
| **Handle** | @TheWardBook (404 = free on 26 Nov 2026) |
| **Tagline** | Every legend comes with rules. Learn them before dark. |
| **Format** | "How to Survive ___ (According to Folklore)". A 2nd-person cold open, then 5 **Wards** (the protective rules the old texts give), each one sourced, then where the legend really comes from, and a verdict |
| **Look** | 16th-century woodcut on candle-lit parchment, IM Fell English + UnifrakturMaguntia type, black ink with one rubric red, dust/snow/ember particles, ink-bleed entrances |
| **Voice** | British male storyteller (Piper `en_GB-alan-medium`, deep, ~98 Hz) with a small stone-room echo and a low wind drone |

## Why this angle (research, 26 Nov 2026)
- **"X explained / origins" is saturated.** Big channels already own it: Extra Mythology (Wendigo 4.9M views), Monstrum/Storied (2.8M), Mysteries of Mythology (Baba Yaga 1.8M, Fairies 1.8M), Jon Solo, Mythology & Fiction Explained, plus "every creature in 12 minutes" list channels.
- **"Rules to survive" has demand but almost no folklore supply.** "Rules of Appalachia" videos get 1–2M views. The folklore survival channels we found ("The Yokai Hour", "Survive The Myth", "Soul Animation") get roughly 100 to 100k views per video and use generic visuals.
- **Our gap:** survival rules taken from *primary folklore texts* (Afanasyev, Grimm, the Peterborough Chronicle, Basil Johnston) instead of creepypasta, with a look nobody in the niche uses (woodcut on parchment).
- **Different from our other 3 lanes:** body science and space "what if" are science, and the scams/heists lane is true crime and money. The reference channel tells human history on white paper with round heads. Ours is legends, on dark parchment with woodcuts.

## Cadence: 4 long videos in month 1, every Wednesday, ~9–10 minutes
- **Why not more?** Every episode has 15–20 sourced claims, and folklore audiences notice errors. Sloppy sourcing kills a mythology channel fast. One a week keeps fact-checking real.
- **Why not fewer?** A new channel needs several videos live before Suggested can learn who watches it. With 4 by Christmas, every new viewer finds a binge-able "chapter".
- **Why ~9–10 min?** Comparable folklore hits run 9–12 minutes (Monstrum ~9, Mysteries of Mythology 15–24). Past 8 minutes we can place mid-roll ads later. Five wards fill 10 minutes with a pattern break every ~60–90 s, and each new Ward card is a natural retention hook.
- **Why Wednesday 21:00 UTC?** It's 4 PM in New York and 9 PM in London, so the video is indexed before US evening and lands in the UK at night, when spooky stories get watched. Wednesday also avoids the Friday upload rush of the bigger history channels.
- **Seasonal pegs:** Krampus goes out 3 days before Krampusnacht (5 Dec). The Wild Hunt goes out 2 days before Christmas, the start of the Twelve Nights. December searches for "Krampus" spike every year.
- **Shorts:** a 45-second vertical cut of each hook every Saturday, linked to the long video. They bring in new viewers.

## Schedule
| Date (21:00 UTC) | Video | Thumbnail A / B |
|---|---|---|
| Wed 2 Dec 2026 | **EP01 How to Survive Krampus** | "December 5th: LOCK THE DOOR" · "He works for A SAINT" |
| Sat 5 Dec (17:00) | Short: Krampus Ward I (on Krampusnacht itself) | |
| Wed 9 Dec | **EP02 How to Survive the Wendigo** | "It is never FULL" · "Sometimes IT'S YOU" |
| Sat 12 Dec | Short: Wendigo hook | |
| Wed 16 Dec | **EP03 How to Survive Baba Yaga** | "Don't ask her TOO MUCH" · "Be kind to HER CAT" |
| Sat 19 Dec | Short: Baba Yaga Ward III (the cat) | |
| Wed 23 Dec | **EP04 How to Survive the Wild Hunt** | "If you hear hounds DON'T LOOK UP" · "Never ANSWER IT" |
| Sat 26 Dec | Short: Wild Hunt Ward III (face down) | |

## Topic bank, ranked by click potential (search interest × visual hook × how well it fits the rules format)
1. **Wendigo** (huge evergreen search) → EP02
2. **Krampus** (big seasonal December spike) → EP01
3. **Baba Yaga** (strong search, and her rules come straight from the tales) → EP03
4. **Kappa** (bow so the water spills from its head: a perfect ward) → month 2
5. **The Wild Hunt** (Yule peg, grows every year with "Rauhnächte" interest) → EP04
6. **Nian** (Lunar New Year, 6 Feb 2027: red, firecrackers, noise) → publish ~3 Feb
7. **Changelings / the Fair Folk** (iron, bread in the pocket, turn your coat inside out)
8. **Churel / Chudail** (South Asian; strong in our home market) and **Aswang** (Philippines)
9. **La Llorona**, **Rusalka**, **Kitsune**, **Draugr**, **Black Shuck**, **Yuki-onna** (Lafcadio Hearn's *Kwaidan*, 1904)
- Handle with care: **Jinn** (living religious belief, needs respectful framing and Islamic scholarship).

## Rules every episode follows
- **Hook (first 30 s):** 2nd person, a time and a place, a sensory threat, the stakes ("you have seconds"), then the promise ("five rules… break one, and, well"), then the title plate.
- **Every ward = a Ward card** (red numeral) + a story from a named source.
- **A twist chapter near the end** (the 1930s ban, the antlers myth, Harlequin), so viewers stay through the last third.
- **The endcard teases the next legend by name,** with its rules hinted.
- **Thumbnails:** one woodcut creature in a candle-lit spot on the left, black on the right, a small bone-white line plus 1–3 big vermilion words. Never repeat the title.

## Week-by-week checklist
- **Before 2 Dec:** create the channel, claim @TheWardBook, upload the branding and the About text (`branding/CHANNEL_SETUP.md`), verify the phone number, upload EP01 as Private, check the ⚠️ items in `scripts/ep01_factcheck.md`.
- **Every Wednesday:** publish, pin the comment, and reply to comments for the first 2 hours.
- **Every Monday:** check click-through rate (aim for 5% or more) and 30-second retention (aim for 65% or more). If click-through is under 3.5% after 48 h, swap the thumbnail manually.
- **End of month:** the EP04 pinned comment asks viewers which legend to open next. Use the top answer for month 2.

## Things only you can do
1. Create the Google/YouTube account and channel. I can't create accounts or post.
2. Upload, schedule, and set **"Altered or synthetic content: Yes"** on every upload.
3. Strongly recommended: re-record the narration with a human voice or a premium TTS. The pipeline takes any voice; swap `VOICE` in `pipeline/film.py`.
4. For EP02, ideally ask an Anishinaabe or Cree viewer to watch it before it goes public.
