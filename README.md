# Channels monitor

Updated 07.11.2026 19:17 Kyiv (17:17 UTC). A pass every 3 hours; known failures are put right by themselves (level 1), a new one seen twice gets an automatic patch (level 2); letters go to the issue **Monitor** only when the owner is needed.

| Channel | | Next 3 slots (local time) | Buffer | Watchdog | Last good build | Topics | What is wrong |
|---|---|---|---|---|---|---|---|
| [What If](https://github.com/edbackulin-eng/whatif-channel) | ✓ | 09.11 15:00 ✓, 10.11 15:00 ✓, 12.11 15:00 ✗ | 2/3 | 0.0 h | 4.1 h | 34 | — |
| [Closed Tabs](https://github.com/edbackulin-eng/closed-tabs) | ✓ | 09.11 17:00 ✓, 10.11 17:00 ✓, 12.11 17:00 ✗ | 2/3 | 0.0 h | 14.1 h | 13 | — |
| [Urzeit (dinosaurs)](https://github.com/edbackulin-eng/prehistoric-channel) | ✗ | 11.11 17:00 ✗, 14.11 17:00 ✗, 18.11 17:00 ✗ | 0/3 | 0.0 h | 3.0 h | 19 | 0 of the next 3 slots have a video (1 waiting for approval or a slot) |
| [Yesterday in Color](https://github.com/edbackulin-eng/archive-channel) | ✗ | 10.11 12:00 ✗, 13.11 12:00 ✗, 17.11 12:00 ✗ | 0/3 | 0.0 h | None h | 20 | 0 of the next 3 slots have a video; no successful build yet; last build failed at prepare / Run python automation/build.py "$SLUG" narrate; 1950s-suburb: qa-failed: match_share; length; thumbnail |
| [Stoic (yt-factory-daily)](https://github.com/beautyapp800-ctrl/yt-factory-daily) | ✓ | 07.11 21:00 ✓, 08.11 21:00 ✓, 09.11 21:00 ✗ | 2/3 | 17.5 h | 0.7 h | generates | — |

**Kaggle GPU, last 7 days:** 10.64 h of 27.5 h (closed-tabs 9.2 h, What If 0.0 h, dinosaurs 1.45 h).

## Journal (last 24 h)

| UTC | Channel | Level | Action | Why | Result |
|---|---|---|---|---|---|
| 11-07 08:13 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-07 05:10 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-07 05:10 | dinosaurs | 2 | autofix | part (#) / render part # | | stopped: The read operation timed out |
| 11-07 05:10 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-07 02:09 | archive | 2 | autofix | prepare / run python automation "$slug" script | | stopped: HTTP Error 503: Service Unavailable |
| 11-07 02:09 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-07 02:09 | closed-tabs | 2 | autofix | resume / render and package | | stopped: HTTP Error 503: Service Unavailable |
| 11-07 02:09 | whatif | 2 | autofix | build / keep two scheduled ahead | | stopped: HTTP Error 503: Service Unavailable |
| 11-06 23:08 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-06 20:07 | archive | 2 | autofix | cut (#) / run python automation "$slug" cut # # | | stopped: HTTP Error 429: Too Many Requests |
| 11-06 20:07 | closed-tabs | 2 | autofix | resume / render and package | | stopped: HTTP Error 429: Too Many Requests |
| 11-06 20:07 | whatif | 2 | autofix | build / keep two scheduled ahead | | stopped: HTTP Error 429: Too Many Requests |
