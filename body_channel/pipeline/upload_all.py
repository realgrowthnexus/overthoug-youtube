"""Combine the four episodes' UPLOAD.md files plus the schedule and settings guide into UPLOAD_ALL.md.
Usage: python3 pipeline/upload_all.py"""
import re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATES = [("Wed 2 Dec", "Fri 4 Dec", "Sun 6 Dec"), ("Wed 9 Dec", "Fri 11 Dec", "Sun 13 Dec"),
         ("Wed 16 Dec", "Fri 18 Dec", "Sun 20 Dec"), ("Wed 23 Dec", "Fri 25 Dec", "Sun 27 Dec")]
out = ["# Your Vitals — every upload in one place (copy and paste)", "",
       "Channel: **Your Vitals** · Handle: **@YourVitals** · All posts go out at **16:00 UTC**, which is **9:00 PM Pakistan**, 11:00 AM New York and 4:00 PM London.", "",
       "## Master schedule (December 2026)", "", "| Date | Time (Pakistan) | What | File | Thumbnail A / B |", "|---|---|---|---|---|"]
for n, (w, f, s) in enumerate(DATES, 1):
    title = re.search(r"## Title\n(.*)\n", open(os.path.join(ROOT, f"episodes/ep0{n}/UPLOAD.md")).read()).group(1)
    out += [f"| **{w}** | 9:00 PM | **EP0{n} long:** {title} | `EP0{n}.mp4` | `thumbs/EP0{n}_A.jpg` / `thumbs/EP0{n}_B.jpg` |",
            f"| {f} | 9:00 PM | EP0{n} Short 1 | `EP0{n}_short1.mp4` | (auto frame) |",
            f"| {s} | 9:00 PM | EP0{n} Short 2 | `EP0{n}_short2.mp4` | (auto frame) |"]
out += ["", "## Settings for every long video (YouTube Studio → Create → Upload videos)", "",
        "1. **Details:** paste the Title and Description from that episode below. **Thumbnail:** upload **A**. Once the video is live, open it and use **Test & Compare** to add **B** as well.",
        "2. **Playlist:** What Happens to Your Body If… (create it once).",
        "3. **Audience:** \"No, it's not made for kids\". **Age restriction:** No.",
        "4. **Show more:**",
        "   - Paid promotion: No",
        "   - **Altered content: YES** (the voice and pictures are AI-made; you have to tick this on every upload)",
        "   - Automatic chapters: On",
        "   - **Tags:** paste the Tags line from that episode below",
        "   - Language: English",
        "   - Caption certification: \"None. Content has never aired on TV in the U.S.\"",
        "   - License: Standard YouTube License",
        "   - Allow embedding: On",
        "   - Publish to Subscriptions feed and notify subscribers: On",
        "   - **Category: Science & Technology**",
        "   - Comments: On, \"Hold potentially inappropriate comments for review\"",
        "5. **Video elements:**",
        "   - **Add subtitles** → Upload file → \"With timing\" → pick that episode's `.srt` file",
        "   - **Add end screen** (the last 20 seconds are made for it): put one video set to \"Best for viewer\" over the empty box on the right, and the **Subscribe** element over the red circle",
        "   - Cards: none for now",
        "6. **Checks:** wait for the copyright check to finish (the music, voice and pictures are all ours, so it should come back clean).",
        "7. **Visibility → Schedule:** set the date from the table above, time **16:00 UTC (9:00 PM Pakistan)**. Upload at least 24 hours early.",
        "8. **When it goes live:** pin the comment listed below and reply to every comment for the first 2 hours.", "",
        "## Settings for every Short", "",
        "- Upload the vertical file (`EP0X_shortN.mp4`). **Title:** that episode's Short line below (the hashtags are already in it). **Description:** `Full video on the channel 👉 @YourVitals #shorts`",
        "- Audience: not made for kids. **Altered content: Yes.** Category: Science & Technology.",
        "- **Related video:** select that episode's long video, so viewers can tap through to it.",
        "- Schedule it for 16:00 UTC (9:00 PM Pakistan) on the Friday or Sunday from the table above.", ""]
for n in range(1, 5):
    s = open(os.path.join(ROOT, f"episodes/ep0{n}/UPLOAD.md")).read()
    s = re.sub(r"^# .*\n", "", s).replace("## ", "### ")
    out += ["---", "", f"## EP0{n}", "", s.strip(), "",
            f"**Files for this episode:** video `EP0{n}.mp4` · subtitles `episodes/ep0{n}/ep0{n}.srt` · Shorts `EP0{n}_short1.mp4`, `EP0{n}_short2.mp4` · thumbnails `thumbs/EP0{n}_A.jpg`, `thumbs/EP0{n}_B.jpg`", ""]
open(os.path.join(ROOT, "UPLOAD_ALL.md"), "w", encoding="utf-8").write("\n".join(out) + "\n"); print("UPLOAD_ALL.md written")
