# Channels monitor

Updated 15.11.2026 16:05 Kyiv (14:05 UTC). A pass every 3 hours; known failures are put right by themselves (level 1), a new one seen twice gets an automatic patch (level 2); letters go to the issue **Monitor** only when the owner is needed.

| Channel | | Next 3 slots (local time) | Buffer | Watchdog | Last good build | Topics | What is wrong |
|---|---|---|---|---|---|---|---|
| [What If](https://github.com/edbackulin-eng/whatif-channel) | ✓ | 16.11 15:00 ✓, 17.11 15:00 ✓, 19.11 15:00 ✗ | 2/3 | 0.0 h | 22.5 h | 29 | — |
| [Closed Tabs](https://github.com/edbackulin-eng/closed-tabs) | ✓ | 16.11 17:00 ✓, 17.11 17:00 ✓, 19.11 17:00 ✓ | 3/3 | 0.0 h | 11.7 h | 10 | — |
| [Urzeit (dinosaurs)](https://github.com/edbackulin-eng/prehistoric-channel) | ✗ | 15.11 17:00 ✓, 18.11 17:00 ✗, 22.11 17:00 ✗ | 1/3 | 0.0 h | 19.3 h | 19 | 1 of the next 3 slots have a video |
| [Yesterday in Color](https://github.com/edbackulin-eng/archive-channel) | ✗ | 17.11 12:00 ✗, 20.11 12:00 ✗, 24.11 12:00 ✗ | 0/3 | 0.0 h | 1.5 h | 10 | 0 of the next 3 slots have a video |
| [Stoic (yt-factory-daily)](https://github.com/beautyapp800-ctrl/yt-factory-daily) | ✓ | 15.11 21:00 ✓, 16.11 21:00 ✗, 17.11 21:00 ✗ | 1/3 | 14.7 h | 6.3 h | generates | — |

**Kaggle GPU, last 7 days:** 10.75 h of 27.5 h (closed-tabs 8.45 h, What If 0.0 h, dinosaurs 2.3 h).

## Journal (last 24 h)

| UTC | Channel | Level | Action | Why | Result |
|---|---|---|---|---|---|
| 11-15 14:05 | dinosaurs | 1 | start episode.yml | 1 of the next 3 slots have a video | started |
| 11-15 11:04 | archive | 2 | autofix autofix/archive-20261115 | the next build passed | kept |
| 11-15 11:04 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-15 08:03 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-15 08:03 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-15 05:02 | archive | 2 | merge autofix/archive-20261115 | smoke on the branch passed | merged into dev; dev goes to main by its smoke |
| 11-15 02:29 | archive | 2 | autofix autofix/archive-20261115 | prepare / run python automation "$slug" narrate | | patch on .github/workflows/episode.yml, smoke started |
| 11-15 02:29 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-15 02:29 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-15 02:29 | closed-tabs | 1 | start topics.yml | 9 topics left | started |
| 11-14 23:26 | archive | 2 | autofix | prepare / run python automation "$slug" narrate | | no patch: Gemini: The error log is missing from the prompt, making it impossible to identi |
| 11-14 23:26 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-14 23:26 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-14 20:20 | archive | 2 | autofix | prepare / run python automation "$slug" narrate | | no patch: Gemini: The error log is missing from the prompt, making it impossible to identi |
| 11-14 20:20 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-14 20:20 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-14 17:19 | archive | 2 | autofix | prepare / run python automation "$slug" narrate | | no patch: the edit does not match the file once |
| 11-14 17:19 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-14 14:14 | archive | 2 | autofix | prepare / run python automation "$slug" narrate | | no patch: the edit does not match the file once |
