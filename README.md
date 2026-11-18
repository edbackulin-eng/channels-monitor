# Channels monitor

Updated 18.11.2026 22:32 Kyiv (20:32 UTC). A pass every 3 hours; known failures are put right by themselves (level 1), a new one seen twice gets an automatic patch (level 2); letters go to the issue **Monitor** only when the owner is needed.

| Channel | | Next 3 slots (local time) | Buffer | Watchdog | Last good build | Topics | What is wrong |
|---|---|---|---|---|---|---|---|
| [What If](https://github.com/edbackulin-eng/whatif-channel) | ✓ | 21.11 15:00 ✓, 24.11 15:00 ✓, 28.11 15:00 ✓ | 3/3 | 0.0 h | 4.4 h | 30 | — |
| [Closed Tabs](https://github.com/edbackulin-eng/closed-tabs) | ✓ | 19.11 17:00 ✓, 23.11 17:00 ✓, 26.11 17:00 ✗ | 2/3 | 0.0 h | 18.2 h | 10 | — |
| [Urzeit (dinosaurs)](https://github.com/edbackulin-eng/prehistoric-channel) | ✗ | 22.11 17:00 ✗, 25.11 17:00 ✗, 29.11 17:00 ✗ | 0/3 | 0.0 h | 97.7 h | 20 | 0 of the next 3 slots have a video; last successful build 97.7 h ago; no video went out on the slot 2026-11-18 16:00 UTC |
| [Yesterday in Color](https://github.com/edbackulin-eng/archive-channel) | ✗ | 20.11 12:00 ✓, 24.11 12:00 ✓, 27.11 12:00 ✗ | 2/3 | 0.0 h | 19.0 h | 8 | 8 topics left (min 10) |
| [Stoic (yt-factory-daily)](https://github.com/beautyapp800-ctrl/yt-factory-daily) | ✓ | 22.11 21:00 ✓, 25.11 21:00 ✗, 29.11 21:00 ✗ | 1/3 | 18.7 h | 0.7 h | generates | — |
| [Moo Toot (yt-kids-daily)](https://github.com/beautyapp800-ctrl/yt-kids-daily) | ✓ | 19.11 16:00 ✓, 22.11 16:00 ✓, 24.11 16:00 ✗ | 2/3 | 18.1 h | 1.4 h | generates | — |
| [America Over Time](https://github.com/edbackulin-eng/map-timelapse) | ✓ | 20.11 20:00 ✓, 23.11 20:00 ✓, 27.11 20:00 ✗ | 2/3 | 2.2 h | 2.2 h | generates | — |
| [Huge To Scale](https://github.com/edbackulin-eng/HugeToScale) | ✗ | 19.11 19:00 ✗, 20.11 19:00 ✗, 21.11 19:00 ✗ | 0/3 | 5.0 h | 2.8 h | 32 | 0 of the next 3 slots have a video; no video went out on the slot 2026-11-18 17:00 UTC; no video went out on the slot 2026-11-17 17:00 UTC |

**Kaggle GPU, last 7 days:** 8.02 h of 27.5 h (closed-tabs 7.08 h, What If 0.0 h, dinosaurs 0.94 h).

## Journal (last 24 h)

| UTC | Channel | Level | Action | Why | Result |
|---|---|---|---|---|---|
| 11-18 20:32 | archive | 2 | autofix | ? | | no patch: the edit does not match the file once |
| 11-18 20:32 | whatif | 2 | autofix | blender (#) / #d shots, share # of # | | no patch: the edit does not match the file once |
| 11-18 17:23 | archive | 2 | autofix | ? | | no patch: the edit does not match the file once |
| 11-18 17:23 | whatif | 2 | autofix | blender (#) / #d shots, share # of # | | no patch: Gemini: The error text and log were not provided in the prompt |
| 11-18 14:27 | archive | 2 | autofix | ? | | no patch: Gemini: The error log was omitted from the prompt, making it impossible to ident |
| 11-18 14:27 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-18 14:27 | whatif | 2 | autofix | blender (#) / #d shots, share # of # | | no patch: the edit does not match the file once |
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
