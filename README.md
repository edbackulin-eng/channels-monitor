# Channels monitor

Updated 20.11.2026 04:29 Kyiv (02:29 UTC). A pass every 3 hours; known failures are put right by themselves (level 1), a new one seen twice gets an automatic patch (level 2); letters go to the issue **Monitor** only when the owner is needed.

| Channel | | Next 3 slots (local time) | Buffer | Watchdog | Last good build | Topics | What is wrong |
|---|---|---|---|---|---|---|---|
| [What If](https://github.com/edbackulin-eng/whatif-channel) | ✓ | 21.11 15:00 ✓, 24.11 15:00 ✓, 28.11 15:00 ✓ | 3/3 | 0.0 h | 10.9 h | 30 | — |
| [Closed Tabs](https://github.com/edbackulin-eng/closed-tabs) | ✓ | 23.11 17:00 ✓, 26.11 17:00 ✓, 30.11 17:00 ✗ | 2/3 | 0.0 h | 0.8 h | 10 | — |
| [Urzeit (dinosaurs)](https://github.com/edbackulin-eng/prehistoric-channel) | ✗ | 22.11 17:00 ✗, 25.11 17:00 ✗, 29.11 17:00 ✗ | 0/3 | 0.0 h | 5.6 h | 18 | 0 of the next 3 slots have a video (2 waiting for approval or a slot); no video went out on the slot 2026-11-18 16:00 UTC |
| [Yesterday in Color](https://github.com/edbackulin-eng/archive-channel) | ✗ | 20.11 12:00 ✓, 24.11 12:00 ✓, 27.11 12:00 ✗ | 2/3 | 0.0 h | 49.0 h | 8 | last successful build 49.0 h ago; 8 topics left (min 10) |
| [Stoic (yt-factory-daily)](https://github.com/beautyapp800-ctrl/yt-factory-daily) | ✓ | 22.11 21:00 ✓, 25.11 21:00 ✗, 29.11 21:00 ✗ | 1/3 | 1.1 h | 7.3 h | generates | — |
| [Moo Toot (yt-kids-daily)](https://github.com/beautyapp800-ctrl/yt-kids-daily) | ✓ | 22.11 16:00 ✓, 24.11 16:00 ✓, 26.11 16:00 ✗ | 2/3 | 0.7 h | 7.2 h | generates | — |
| [America Over Time](https://github.com/edbackulin-eng/map-timelapse) | ✓ | 20.11 20:00 ✓, 23.11 20:00 ✓, 27.11 20:00 ✗ | 2/3 | 6.9 h | 6.9 h | generates | — |
| [Huge To Scale](https://github.com/edbackulin-eng/HugeToScale) | ✗ | 20.11 19:00 ✓, 21.11 19:00 ✓, 22.11 19:00 ✗ | 2/3 | 4.4 h | 4.4 h | 31 | last build failed at render / render (ladder_volcanoes, 3, 280, 370, blender) / render frames 280-370; no video went out on the slot 2026-11-18 17:00 UTC |

**Kaggle GPU, last 7 days:** 8.04 h of 27.5 h (closed-tabs 7.68 h, What If 0.0 h, dinosaurs 0.36 h).

## Journal (last 24 h)

| UTC | Channel | Level | Action | Why | Result |
|---|---|---|---|---|---|
| 11-20 02:29 | archive | 2 | autofix | ? | | no patch: the edit does not match the file once |
| 11-20 02:29 | dinosaurs | 2 | autofix | prepare / german narration, #.#d layers, species check, plan, footage, voice lines | | no patch: the edit does not match the file once |
| 11-20 02:29 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-20 02:29 | whatif | 2 | autofix | blender (#) / #d shots, share # of # | | no patch: Gemini: No error log was provided to identify the failure. |
| 11-19 23:24 | archive | 2 | autofix | ? | | no patch: Gemini: No failure log was provided, so the failure cannot be identified with ce |
| 11-19 23:24 | dinosaurs | 2 | autofix | prepare / german narration, #.#d layers, species check, plan, footage, voice lines | | no patch: Gemini: No error log was provided under THE FAILURE, making it impossible to det |
| 11-19 23:24 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-19 23:24 | whatif | 2 | autofix | blender (#) / #d shots, share # of # | | no patch: Gemini: The failure log is empty, so the failure cannot be determined with certa |
| 11-19 20:16 | archive | 2 | autofix | ? | | no patch: the edit does not match the file once |
| 11-19 20:16 | dinosaurs | 2 | autofix | prepare / german narration, #.#d layers, species check, plan, footage, voice lines | | no patch: Gemini: The failure log was not provided in the prompt. |
| 11-19 20:16 | closed-tabs | 1 | start topics.yml | 9 topics left | started |
| 11-19 20:16 | whatif | 2 | autofix | blender (#) / #d shots, share # of # | | no patch: the edit does not match the file once |
| 11-19 17:13 | archive | 2 | autofix | ? | | no patch: the edit does not match the file once |
| 11-19 17:13 | dinosaurs | 2 | autofix | prepare / german narration, #.#d layers, species check, plan, footage, voice lines | | no patch: the edit does not match the file once |
| 11-19 17:13 | whatif | 2 | autofix | blender (#) / #d shots, share # of # | | no patch: the edit does not match the file once |
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
