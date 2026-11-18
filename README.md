# Channels monitor

Updated 18.11.2026 13:18 Kyiv (11:18 UTC). A pass every 3 hours; known failures are put right by themselves (level 1), a new one seen twice gets an automatic patch (level 2); letters go to the issue **Monitor** only when the owner is needed.

| Channel | | Next 3 slots (local time) | Buffer | Watchdog | Last good build | Topics | What is wrong |
|---|---|---|---|---|---|---|---|
| [What If](https://github.com/edbackulin-eng/whatif-channel) | ✗ | 21.11 15:00 ✓, 24.11 15:00 ✗, 28.11 15:00 ✗ | 1/3 | 0.0 h | 15.1 h | 30 | 1 of the next 3 slots have a video; last build failed at blender (5) / 3D shots, share 5 of 8 |
| [Closed Tabs](https://github.com/edbackulin-eng/closed-tabs) | ✓ | 19.11 17:00 ✓, 23.11 17:00 ✓, 26.11 17:00 ✗ | 2/3 | 0.0 h | 9.0 h | 10 | — |
| [Urzeit (dinosaurs)](https://github.com/edbackulin-eng/prehistoric-channel) | ✗ | 18.11 17:00 ✗, 22.11 17:00 ✗, 25.11 17:00 ✗ | 0/3 | 0.0 h | 88.5 h | 20 | 0 of the next 3 slots have a video; last successful build 88.5 h ago |
| [Yesterday in Color](https://github.com/edbackulin-eng/archive-channel) | ✗ | 20.11 12:00 ✓, 24.11 12:00 ✓, 27.11 12:00 ✗ | 2/3 | 0.0 h | 9.8 h | 8 | 8 topics left (min 10) |
| [Stoic (yt-factory-daily)](https://github.com/beautyapp800-ctrl/yt-factory-daily) | ✓ | 18.11 21:00 ✓, 22.11 21:00 ✗, 25.11 21:00 ✗ | 1/3 | 9.5 h | 2.8 h | generates | — |
| [Moo Toot (yt-kids-daily)](https://github.com/beautyapp800-ctrl/yt-kids-daily) | ✓ | 19.11 16:00 ✓, 22.11 16:00 ✓, 24.11 16:00 ✗ | 2/3 | 8.9 h | 0.8 h | generates | — |
| [America Over Time](https://github.com/edbackulin-eng/map-timelapse) | ✗ | 20.11 20:00 ✗, 23.11 20:00 ✗, 27.11 20:00 ✗ | 0/3 | 1.4 h | 0.3 h | generates | 0 of the next 3 slots have a video; no video went out on the slot 2026-11-16 18:00 UTC |

**Kaggle GPU, last 7 days:** 8.68 h of 27.5 h (closed-tabs 7.08 h, What If 0.0 h, dinosaurs 1.6 h).

## Journal (last 24 h)

| UTC | Channel | Level | Action | Why | Result |
|---|---|---|---|---|---|
| 11-18 11:18 | archive | 2 | autofix | ? | | no patch: Gemini: The error log is missing from the prompt, so the exact failure cannot be |
| 11-18 11:18 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-18 11:18 | whatif | 2 | autofix | blender (#) / #d shots, share # of # | | no patch: Gemini: The failure log is empty, so the exact error in the blender step cannot  |
| 11-18 08:17 | archive | 2 | autofix | ? | | no patch: Gemini: No failure log provided to identify the error. |
| 11-18 08:17 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-18 08:17 | closed-tabs | 1 | start topics.yml | 9 topics left | started |
| 11-18 05:10 | archive | 2 | autofix | ? | | no patch: the edit does not match the file once |
| 11-18 05:10 | whatif | 1 | start build-video.yml | 0 of the next 3 slots have a video | started |
| 11-18 02:17 | archive | 2 | autofix | ? | | no patch: the edit does not match the file once |
| 11-18 02:17 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-17 23:08 | archive | 2 | autofix | ? | | no patch: the edit does not match the file once |
| 11-17 23:08 | archive | 1 | start episode.yml | 1 of the next 3 slots have a video | started |
| 11-17 23:08 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-17 23:08 | closed-tabs | 1 | start daily.yml | 1 of the next 3 slots have a video | started |
| 11-17 20:07 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-17 20:07 | closed-tabs | 1 | start daily.yml | 1 of the next 3 slots have a video | started |
| 11-17 20:07 | closed-tabs | 1 | start topics.yml | 9 topics left | started |
| 11-17 17:06 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-17 14:05 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-17 14:05 | whatif | 1 | start build-video.yml | 1 of the next 3 slots have a video | started |
