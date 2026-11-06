# Channels monitor

Updated 06.11.2026 04:15 Kyiv (02:15 UTC). A pass every 3 hours; known failures are put right by themselves (level 1), a new one seen twice gets an automatic patch (level 2); letters go to the issue **Monitor** only when the owner is needed.

| Channel | | Next 3 slots (local time) | Buffer | Watchdog | Last good build | Topics | What is wrong |
|---|---|---|---|---|---|---|---|
| [What If](https://github.com/edbackulin-eng/whatif-channel) | ✓ | 06.11 15:00 ✓, 07.11 15:00 ✓, 09.11 15:00 ✗ | 2/3 | 0.0 h | 11.7 h | 36 | — |
| [Closed Tabs](https://github.com/edbackulin-eng/closed-tabs) | ✓ | 06.11 17:00 ✓, 07.11 17:00 ✓, 09.11 17:00 ✓ | 3/3 | 0.0 h | 1.3 h | 14 | — |
| [Urzeit (dinosaurs)](https://github.com/edbackulin-eng/prehistoric-channel) | ✗ | 07.11 17:00 ✗, 11.11 17:00 ✗, 14.11 17:00 ✗ | 0/3 | 0.0 h | 36.3 h | 19 | 0 of the next 3 slots have a video; last successful build 36.3 h ago; last build failed at part (7) / Render part 7; lebende-fossilien: qa-failed: hook; subject; pace; music; first_min; motion; dinosaurs; wow |
| [Yesterday in Color](https://github.com/edbackulin-eng/archive-channel) | ✗ | 06.11 12:00 ✗, 10.11 12:00 ✗, 13.11 12:00 ✗ | 0/3 | 0.0 h | None h | 20 | 0 of the next 3 slots have a video; no successful build yet; last build failed at cut (4) / Run python automation/build.py "$SLUG" cut 4 8 |
| [Stoic (yt-factory-daily)](https://github.com/beautyapp800-ctrl/yt-factory-daily) | ✓ | 06.11 21:00 ✓, 07.11 21:00 ✗, 08.11 21:00 ✗ | 1/3 | 1.7 h | 8.0 h | generates | — |

**Kaggle GPU, last 7 days:** 10.57 h of 27.5 h (closed-tabs 9.12 h, What If 0.0 h, dinosaurs 1.45 h).

## Journal (last 24 h)

| UTC | Channel | Level | Action | Why | Result |
|---|---|---|---|---|---|
| 11-05 20:13 | closed-tabs | 1 | planned daily.yml | owner 05.11: the build for 07.11 starts at 20:00 UTC with the full stills budget | already running |
| 11-05 16:11 | whatif | 1 | runbook |  | stopped: HTTP Error 500: Internal Server Error |
