# Channels monitor

Updated 08.11.2026 04:20 Kyiv (02:20 UTC). A pass every 3 hours; known failures are put right by themselves (level 1), a new one seen twice gets an automatic patch (level 2); letters go to the issue **Monitor** only when the owner is needed.

| Channel | | Next 3 slots (local time) | Buffer | Watchdog | Last good build | Topics | What is wrong |
|---|---|---|---|---|---|---|---|
| [What If](https://github.com/edbackulin-eng/whatif-channel) | ✓ | 09.11 15:00 ✓, 10.11 15:00 ✓, 12.11 15:00 ✗ | 2/3 | 0.0 h | 13.2 h | 34 | — |
| [Closed Tabs](https://github.com/edbackulin-eng/closed-tabs) | ✓ | 09.11 17:00 ✓, 10.11 17:00 ✓, 12.11 17:00 ✗ | 2/3 | 0.0 h | 23.1 h | 13 | — |
| [Urzeit (dinosaurs)](https://github.com/edbackulin-eng/prehistoric-channel) | ✗ | 08.11 17:00 ✓, 11.11 17:00 ✗, 15.11 17:00 ✗ | 1/3 | 0.0 h | 12.0 h | 20 | 1 of the next 3 slots have a video |
| [Yesterday in Color](https://github.com/edbackulin-eng/archive-channel) | ✗ | 10.11 12:00 ✗, 13.11 12:00 ✗, 17.11 12:00 ✗ | 0/3 | 0.0 h | None h | 20 | 0 of the next 3 slots have a video; no successful build yet; last build failed at prepare / Run python automation/build.py "$SLUG" script; 1950s-suburb: qa-failed: repeats; thumbnail |
| [Stoic (yt-factory-daily)](https://github.com/beautyapp800-ctrl/yt-factory-daily) | ✓ | 08.11 21:00 ✓, 09.11 21:00 ✗, 10.11 21:00 ✗ | 1/3 | 3.4 h | 9.7 h | generates | — |

**Kaggle GPU, last 7 days:** 11.5 h of 27.5 h (closed-tabs 9.36 h, What If 0.0 h, dinosaurs 2.14 h).

## Journal (last 24 h)

| UTC | Channel | Level | Action | Why | Result |
|---|---|---|---|---|---|
| 11-08 02:20 | archive | 2 | autofix | prepare / run python automation "$slug" script | | no patch: Gemini: No failure log was provided to diagnose the failure. |
| 11-08 02:20 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-08 02:20 | dinosaurs | 2 | autofix | part (#) / render part # | | no patch: Gemini: no failure log was provided to identify the error |
| 11-08 02:20 | dinosaurs | 1 | start episode.yml | 1 of the next 3 slots have a video | started |
| 11-07 23:19 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-07 23:19 | dinosaurs | 1 | start episode.yml | 1 of the next 3 slots have a video | started |
| 11-07 08:13 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-07 05:10 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-07 05:10 | dinosaurs | 2 | autofix | part (#) / render part # | | stopped: The read operation timed out |
| 11-07 05:10 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
