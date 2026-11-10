# Channels monitor

Updated 10.11.2026 04:25 Kyiv (02:25 UTC). A pass every 3 hours; known failures are put right by themselves (level 1), a new one seen twice gets an automatic patch (level 2); letters go to the issue **Monitor** only when the owner is needed.

| Channel | | Next 3 slots (local time) | Buffer | Watchdog | Last good build | Topics | What is wrong |
|---|---|---|---|---|---|---|---|
| [What If](https://github.com/edbackulin-eng/whatif-channel) | ✓ | 10.11 15:00 ✓, 12.11 15:00 ✓, 13.11 15:00 ✗ | 2/3 | 0.0 h | 9.9 h | 33 | — |
| [Closed Tabs](https://github.com/edbackulin-eng/closed-tabs) | ✓ | 10.11 17:00 ✓, 12.11 17:00 ✓, 13.11 17:00 ✗ | 2/3 | 0.0 h | 26.8 h | 12 | — |
| [Urzeit (dinosaurs)](https://github.com/edbackulin-eng/prehistoric-channel) | ✗ | 11.11 17:00 ✗, 15.11 17:00 ✗, 18.11 17:00 ✗ | 0/3 | 0.0 h | 60.1 h | 20 | 0 of the next 3 slots have a video; last successful build 60.1 h ago |
| [Yesterday in Color](https://github.com/edbackulin-eng/archive-channel) | ✗ | 10.11 12:00 ✗, 13.11 12:00 ✗, 17.11 12:00 ✗ | 0/3 | 0.0 h | 3.0 h | 18 | 0 of the next 3 slots have a video; 1950s-suburb: qa-failed: repeats; thumbnail |
| [Stoic (yt-factory-daily)](https://github.com/beautyapp800-ctrl/yt-factory-daily) | ✓ | 10.11 21:00 ✓, 11.11 21:00 ✗, 12.11 21:00 ✗ | 1/3 | 0.1 h | 5.4 h | generates | — |

**Kaggle GPU, last 7 days:** 11.5 h of 27.5 h (closed-tabs 9.36 h, What If 0.0 h, dinosaurs 2.14 h).

## Journal (last 24 h)

| UTC | Channel | Level | Action | Why | Result |
|---|---|---|---|---|---|
| 11-10 02:25 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-10 02:25 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-09 23:24 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-09 23:24 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-09 20:23 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-09 20:23 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-09 17:22 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-09 14:21 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-09 14:21 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-09 11:11 | archive | 2 | autofix | prepare / run python automation "$slug" narrate | | no patch: Gemini: The error text is missing from the prompt. |
| 11-09 11:11 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-09 11:11 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-09 08:02 | archive | 2 | autofix | prepare / run python automation "$slug" narrate | | no patch: Gemini: No failure log was provided, so the cause of the failure cannot be deter |
| 11-09 08:02 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-09 08:02 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-09 05:01 | archive | 2 | autofix | prepare / run python automation "$slug" narrate | | no patch: the edit does not match the file once |
| 11-09 02:29 | archive | 2 | autofix | prepare / run python automation "$slug" narrate | | no patch: Gemini: The failure log is empty, so the error in the narrate step cannot be det |
| 11-09 02:29 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-09 02:29 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
