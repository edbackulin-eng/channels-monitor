# Channels monitor

Updated 19.11.2026 16:17 Kyiv (14:17 UTC). A pass every 3 hours; known failures are put right by themselves (level 1), a new one seen twice gets an automatic patch (level 2); letters go to the issue **Monitor** only when the owner is needed.

| Channel | | Next 3 slots (local time) | Buffer | Watchdog | Last good build | Topics | What is wrong |
|---|---|---|---|---|---|---|---|
| [What If](https://github.com/edbackulin-eng/whatif-channel) | ✓ | 21.11 15:00 ✓, 24.11 15:00 ✓, 28.11 15:00 ✓ | 3/3 | 0.0 h | 22.1 h | 30 | — |
| [Closed Tabs](https://github.com/edbackulin-eng/closed-tabs) | ✓ | 19.11 17:00 ✓, 23.11 17:00 ✓, 26.11 17:00 ✗ | 2/3 | 0.0 h | 12.4 h | 10 | — |
| [Urzeit (dinosaurs)](https://github.com/edbackulin-eng/prehistoric-channel) | ✗ | 22.11 17:00 ✗, 25.11 17:00 ✗, 29.11 17:00 ✗ | 0/3 | 0.0 h | 115.5 h | 20 | 0 of the next 3 slots have a video; last successful build 115.5 h ago; last build failed at prepare / German narration, 2.5D layers, species check, plan, footage, voice lines; no video went out on the slot 2026-11-18 16:00 UTC |
| [Yesterday in Color](https://github.com/edbackulin-eng/archive-channel) | ✗ | 20.11 12:00 ✓, 24.11 12:00 ✓, 27.11 12:00 ✗ | 2/3 | 0.0 h | 36.8 h | 8 | last successful build 36.8 h ago; 8 topics left (min 10) |
| [Stoic (yt-factory-daily)](https://github.com/beautyapp800-ctrl/yt-factory-daily) | ✓ | 22.11 21:00 ✓, 25.11 21:00 ✗, 29.11 21:00 ✗ | 1/3 | 12.8 h | 5.5 h | generates | — |
| [Moo Toot (yt-kids-daily)](https://github.com/beautyapp800-ctrl/yt-kids-daily) | ✓ | 22.11 16:00 ✓, 24.11 16:00 ✗, 26.11 16:00 ✗ | 1/3 | 12.4 h | 3.7 h | generates | — |
| [America Over Time](https://github.com/edbackulin-eng/map-timelapse) | ✓ | 20.11 20:00 ✓, 23.11 20:00 ✓, 27.11 20:00 ✗ | 2/3 | 19.9 h | 6.2 h | generates | — |
| [Huge To Scale](https://github.com/edbackulin-eng/HugeToScale) | ✗ | 19.11 19:00 ✓, 20.11 19:00 ✓, 21.11 19:00 ✗ | 2/3 | 16.5 h | 16.5 h | 31 | last build failed at render / render (ladder_volcanoes, 2, 187, 279, blender) / render frames 187-279; no video went out on the slot 2026-11-18 17:00 UTC; no video went out on the slot 2026-11-17 17:00 UTC |

**Kaggle GPU, last 7 days:** 8.02 h of 27.5 h (closed-tabs 7.08 h, What If 0.0 h, dinosaurs 0.94 h).

## Journal (last 24 h)

| UTC | Channel | Level | Action | Why | Result |
|---|---|---|---|---|---|
| 11-19 14:17 | archive | 2 | autofix | ? | | no patch: the edit does not match the file once |
| 11-19 14:17 | dinosaurs | 2 | autofix | prepare / german narration, #.#d layers, species check, plan, footage, voice lines | | waiting: no model answered - gemini-flash-latest: the day's quota is spent; gemini-flash-l |
| 11-19 14:17 | whatif | 2 | autofix | blender (#) / #d shots, share # of # | | no patch: the edit does not match the file once |
| 11-19 11:20 | archive | 2 | autofix | ? | | no patch: Gemini: No failure log was provided, so the failing step and error cannot be ide |
| 11-19 11:20 | whatif | 2 | autofix | blender (#) / #d shots, share # of # | | no patch: the edit does not match the file once |
| 11-19 08:16 | archive | 2 | autofix | ? | | no patch: Gemini: No error log was provided to diagnose the exact failure. |
| 11-19 08:16 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-19 08:16 | whatif | 2 | autofix | blender (#) / #d shots, share # of # | | no patch: the edit does not match the file once |
| 11-19 05:12 | archive | 2 | autofix | ? | | no patch: the edit does not match the file once |
| 11-19 05:12 | whatif | 2 | autofix | blender (#) / #d shots, share # of # | | no patch: the edit does not match the file once |
| 11-19 02:38 | archive | 2 | autofix | ? | | no patch: the edit does not match the file once |
| 11-19 02:38 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-19 02:38 | whatif | 2 | autofix | blender (#) / #d shots, share # of # | | no patch: the edit does not match the file once |
| 11-18 23:35 | archive | 2 | autofix | ? | | no patch: Gemini: The error log was omitted from the prompt, making it impossible to ident |
| 11-18 23:35 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-18 23:35 | whatif | 2 | autofix | blender (#) / #d shots, share # of # | | no patch: the edit does not match the file once |
| 11-18 20:32 | archive | 2 | autofix | ? | | no patch: the edit does not match the file once |
| 11-18 20:32 | whatif | 2 | autofix | blender (#) / #d shots, share # of # | | no patch: the edit does not match the file once |
| 11-18 17:23 | archive | 2 | autofix | ? | | no patch: the edit does not match the file once |
| 11-18 17:23 | whatif | 2 | autofix | blender (#) / #d shots, share # of # | | no patch: Gemini: The error text and log were not provided in the prompt |
| 11-18 14:27 | archive | 2 | autofix | ? | | no patch: Gemini: The error log was omitted from the prompt, making it impossible to ident |
| 11-18 14:27 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-18 14:27 | whatif | 2 | autofix | blender (#) / #d shots, share # of # | | no patch: the edit does not match the file once |
