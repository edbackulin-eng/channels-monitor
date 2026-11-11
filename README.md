# Channels monitor

Updated 11.11.2026 16:14 Kyiv (14:14 UTC). A pass every 3 hours; known failures are put right by themselves (level 1), a new one seen twice gets an automatic patch (level 2); letters go to the issue **Monitor** only when the owner is needed.

| Channel | | Next 3 slots (local time) | Buffer | Watchdog | Last good build | Topics | What is wrong |
|---|---|---|---|---|---|---|---|
| [What If](https://github.com/edbackulin-eng/whatif-channel) | ✓ | 12.11 15:00 ✓, 13.11 15:00 ✓, 14.11 15:00 ✗ | 2/3 | 0.0 h | 22.7 h | 32 | — |
| [Closed Tabs](https://github.com/edbackulin-eng/closed-tabs) | ✓ | 12.11 17:00 ✓, 13.11 17:00 ✓, 14.11 17:00 ✓ | 3/3 | 0.0 h | 10.8 h | 10 | — |
| [Urzeit (dinosaurs)](https://github.com/edbackulin-eng/prehistoric-channel) | ✗ | 11.11 17:00 ✗, 15.11 17:00 ✗, 18.11 17:00 ✗ | 0/3 | 0.0 h | 95.9 h | 20 | 0 of the next 3 slots have a video; last successful build 95.9 h ago |
| [Yesterday in Color](https://github.com/edbackulin-eng/archive-channel) | ✗ | 13.11 12:00 ✗, 17.11 12:00 ✗, 20.11 12:00 ✗ | 0/3 | 0.0 h | 11.9 h | 11 | 0 of the next 3 slots have a video; last build failed at render / Run python automation/build.py "$SLUG" render; 1950s-suburb: qa-failed: repeats; thumbnail |
| [Stoic (yt-factory-daily)](https://github.com/beautyapp800-ctrl/yt-factory-daily) | ✓ | 11.11 21:00 ✓, 12.11 21:00 ✓, 13.11 21:00 ✗ | 2/3 | 14.0 h | 5.9 h | generates | — |

**Kaggle GPU, last 7 days:** 13.81 h of 27.5 h (closed-tabs 12.41 h, What If 0.0 h, dinosaurs 1.4 h).

## Journal (last 24 h)

| UTC | Channel | Level | Action | Why | Result |
|---|---|---|---|---|---|
| 11-11 14:14 | archive | 2 | autofix | prepare / run python automation "$slug" script | | no patch: the edit does not match the file once |
| 11-11 14:14 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-11 11:12 | archive | 2 | autofix | prepare / run python automation "$slug" script | | no patch: Gemini: No failure log provided to identify the error |
| 11-11 08:08 | archive | 2 | autofix | prepare / run python automation "$slug" script | | no patch: Gemini: No error log was provided, so the cause of failure cannot be determined. |
| 11-11 05:07 | archive | 2 | autofix | prepare / run python automation "$slug" script | | no patch: Gemini: No failure log was provided, so the exact error and its cause cannot be  |
| 11-11 02:21 | archive | 2 | autofix | prepare / run python automation "$slug" script | | no patch: the edit does not match the file once |
| 11-11 02:21 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-11 02:21 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-10 23:19 | archive | 2 | autofix | prepare / run python automation "$slug" script | | no patch: the edit does not match the file once |
| 11-10 23:19 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-10 23:19 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-10 20:17 | archive | 2 | autofix | prepare / run python automation "$slug" script | | no patch: the edit does not match the file once |
| 11-10 20:17 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-10 20:17 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-10 17:15 | archive | 2 | autofix | prepare / run python automation "$slug" script | | no patch: the edit does not match the file once |
