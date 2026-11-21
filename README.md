# Channels monitor

Updated 21.11.2026 16:22 Kyiv (14:22 UTC). A pass every 3 hours; known failures are put right by themselves (level 1), a new one seen twice gets an automatic patch (level 2); letters go to the issue **Monitor** only when the owner is needed.

| Channel | | Next 3 slots (local time) | Buffer | Watchdog | Last good build | Topics | What is wrong |
|---|---|---|---|---|---|---|---|
| [What If](https://github.com/edbackulin-eng/whatif-channel) | ✓ | 21.11 15:00 ✓, 24.11 15:00 ✓, 28.11 15:00 ✓ | 3/3 | 0.0 h | 0.7 h | 30 | — |
| [Closed Tabs](https://github.com/edbackulin-eng/closed-tabs) | ✓ | 23.11 17:00 ✓, 26.11 17:00 ✓, 30.11 17:00 ✗ | 2/3 | 0.0 h | 13.0 h | 10 | — |
| [Urzeit (dinosaurs)](https://github.com/edbackulin-eng/prehistoric-channel) | ✗ | 22.11 17:00 ✗, 25.11 17:00 ✗, 29.11 17:00 ✗ | 0/3 | 0.0 h | 41.5 h | 18 | 0 of the next 3 slots have a video (2 waiting for approval or a slot); last successful build 41.5 h ago |
| [Yesterday in Color](https://github.com/edbackulin-eng/archive-channel) | ✗ | 24.11 12:00 ✓, 27.11 12:00 ✓, 01.12 12:00 ✗ | 2/3 | 0.0 h | 17.9 h | 8 | 8 topics left (min 10) |
| [Stoic (yt-factory-daily)](https://github.com/beautyapp800-ctrl/yt-factory-daily) | ✓ | 22.11 21:00 ✓, 25.11 21:00 ✗, 29.11 21:00 ✗ | 1/3 | 13.4 h | 6.1 h | generates | — |
| [Moo Toot (yt-kids-daily)](https://github.com/beautyapp800-ctrl/yt-kids-daily) | ✓ | 22.11 16:00 ✓, 24.11 16:00 ✓, 26.11 16:00 ✗ | 2/3 | 12.8 h | 4.4 h | generates | — |
| [America Over Time](https://github.com/edbackulin-eng/map-timelapse) | ✗ | 23.11 20:00 ✓, 27.11 20:00 ✓, 30.11 20:00 ✗ | 2/3 | 19.2 h | 42.8 h | generates | last successful build 42.8 h ago; last build failed at upload / Upload next reserve video |
| [Huge To Scale](https://github.com/edbackulin-eng/HugeToScale) | ✗ | 21.11 19:00 ✓, 22.11 19:00 ✗, 23.11 19:00 ✗ | 1/3 | 16.6 h | 16.6 h | 31 | 1 of the next 3 slots have a video; last build failed at render / render (ladder_volcanoes, 2, 187, 279, blender) / render frames 187-279 |

**Kaggle GPU, last 7 days:** 5.43 h of 27.5 h (closed-tabs 5.43 h, What If 0.0 h, dinosaurs 0.0 h).

## Journal (last 24 h)

| UTC | Channel | Level | Action | Why | Result |
|---|---|---|---|---|---|
| 11-21 14:22 | dinosaurs | 2 | autofix | prepare / german narration, #.#d layers, species check, plan, footage, voice lines | | no patch: Gemini: The failure log is empty, so the exact error message and failing line ca |
| 11-21 14:22 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-21 11:16 | dinosaurs | 2 | autofix | prepare / german narration, #.#d layers, species check, plan, footage, voice lines | | no patch: the edit does not match the file once |
| 11-21 11:16 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-21 08:12 | dinosaurs | 2 | autofix | prepare / german narration, #.#d layers, species check, plan, footage, voice lines | | no patch: Gemini: No failure log was provided, so the cause cannot be determined with cert |
| 11-21 08:12 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-21 08:12 | whatif | 2 | autofix | blender (#) / #d shots, share # of # | | no patch: Gemini: No error log was provided to identify the cause of the failure. |
| 11-21 05:08 | dinosaurs | 2 | autofix | prepare / german narration, #.#d layers, species check, plan, footage, voice lines | | no patch: the edit does not match the file once |
| 11-21 05:08 | whatif | 2 | autofix | blender (#) / #d shots, share # of # | | no patch: the edit does not match the file once |
| 11-21 02:30 | dinosaurs | 2 | autofix | prepare / german narration, #.#d layers, species check, plan, footage, voice lines | | no patch: the edit does not match the file once |
| 11-21 02:30 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-21 02:30 | whatif | 2 | autofix | blender (#) / #d shots, share # of # | | no patch: the edit does not match the file once |
| 11-20 23:28 | dinosaurs | 2 | autofix | prepare / german narration, #.#d layers, species check, plan, footage, voice lines | | no patch: the edit does not match the file once |
| 11-20 23:28 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-20 23:28 | whatif | 2 | autofix | blender (#) / #d shots, share # of # | | no patch: Gemini: No error log was provided to identify the failure in the step. |
| 11-20 20:26 | archive | 2 | autofix | ? | | no patch: Gemini: No error log was provided to diagnose the specific failure in the workfl |
| 11-20 20:26 | dinosaurs | 2 | autofix | prepare / german narration, #.#d layers, species check, plan, footage, voice lines | | no patch: the edit does not match the file once |
| 11-20 20:26 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-20 20:26 | whatif | 2 | autofix | blender (#) / #d shots, share # of # | | no patch: the edit does not match the file once |
| 11-20 17:24 | archive | 2 | autofix | ? | | no patch: the edit does not match the file once |
| 11-20 17:24 | dinosaurs | 2 | autofix | prepare / german narration, #.#d layers, species check, plan, footage, voice lines | | no patch: the edit does not match the file once |
| 11-20 17:24 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-20 17:24 | whatif | 2 | autofix | blender (#) / #d shots, share # of # | | no patch: the edit does not match the file once |
