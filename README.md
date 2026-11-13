# Channels monitor

Updated 14.11.2026 01:24 Kyiv (23:24 UTC). A pass every 3 hours; known failures are put right by themselves (level 1), a new one seen twice gets an automatic patch (level 2); letters go to the issue **Monitor** only when the owner is needed.

| Channel | | Next 3 slots (local time) | Buffer | Watchdog | Last good build | Topics | What is wrong |
|---|---|---|---|---|---|---|---|
| [What If](https://github.com/edbackulin-eng/whatif-channel) | ✓ | 14.11 15:00 ✓, 16.11 15:00 ✓, 17.11 15:00 ✗ | 2/3 | 0.0 h | 9.7 h | 30 | — |
| [Closed Tabs](https://github.com/edbackulin-eng/closed-tabs) | ✓ | 14.11 17:00 ✓, 16.11 17:00 ✓, 17.11 17:00 ✗ | 2/3 | 0.0 h | 19.9 h | 10 | — |
| [Urzeit (dinosaurs)](https://github.com/edbackulin-eng/prehistoric-channel) | ✗ | 15.11 17:00 ✗, 18.11 17:00 ✗, 22.11 17:00 ✗ | 0/3 | 0.0 h | 38.9 h | 19 | 0 of the next 3 slots have a video; last successful build 38.9 h ago; megalodon: qa-failed: hook; subject; pace; music; motion; dinosaurs; scenes; match; consistent; viewer |
| [Yesterday in Color](https://github.com/edbackulin-eng/archive-channel) | ✗ | 17.11 12:00 ✗, 20.11 12:00 ✗, 24.11 12:00 ✗ | 0/3 | 0.0 h | 3.0 h | 11 | 0 of the next 3 slots have a video |
| [Stoic (yt-factory-daily)](https://github.com/beautyapp800-ctrl/yt-factory-daily) | ✓ | 14.11 21:00 ✓, 15.11 21:00 ✗, 16.11 21:00 ✗ | 1/3 | 22.7 h | 5.4 h | generates | — |

**Kaggle GPU, last 7 days:** 11.81 h of 27.5 h (closed-tabs 8.81 h, What If 0.0 h, dinosaurs 3.0 h).

## Journal (last 24 h)

| UTC | Channel | Level | Action | Why | Result |
|---|---|---|---|---|---|
| 11-13 23:24 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-13 20:23 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-13 17:15 | archive | 2 | autofix | prepare / plan the shots (a topic with under # min of confirmed film is deferred, the next | no patch: the edit does not match the file once |
| 11-13 17:15 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-13 17:15 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-13 14:14 | archive | 2 | autofix | prepare / plan the shots (a topic with under # min of confirmed film is deferred, the next | no patch: Gemini: The error log is missing, so the exact failure and failing line cannot b |
| 11-13 14:14 | archive | 1 | start episode.yml | 1 of the next 3 slots have a video | started |
| 11-13 14:14 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-13 14:14 | closed-tabs | 1 | start watchdog.yml | hung | started |
| 11-13 14:14 | closed-tabs | 1 | cancel watchdog.yml run 43379187798 | running 7.7 h (limit 6.2 h) | cancelled |
| 11-13 11:13 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-13 08:12 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-13 08:12 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-13 05:11 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-13 05:11 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-13 05:11 | closed-tabs | 1 | start topics.yml | 9 topics left | started |
| 11-13 02:10 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-13 02:10 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
