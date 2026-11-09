# Channels monitor

Updated 09.11.2026 07:01 Kyiv (05:01 UTC). A pass every 3 hours; known failures are put right by themselves (level 1), a new one seen twice gets an automatic patch (level 2); letters go to the issue **Monitor** only when the owner is needed.

| Channel | | Next 3 slots (local time) | Buffer | Watchdog | Last good build | Topics | What is wrong |
|---|---|---|---|---|---|---|---|
| [What If](https://github.com/edbackulin-eng/whatif-channel) | ✗ | 09.11 15:00 ✓, 10.11 15:00 ✓, 12.11 15:00 ✗ | 2/3 | 0.0 h | 39.9 h | 34 | last successful build 39.9 h ago |
| [Closed Tabs](https://github.com/edbackulin-eng/closed-tabs) | ✓ | 09.11 17:00 ✓, 10.11 17:00 ✓, 12.11 17:00 ✓ | 3/3 | 0.0 h | 5.4 h | 12 | — |
| [Urzeit (dinosaurs)](https://github.com/edbackulin-eng/prehistoric-channel) | ✗ | 11.11 17:00 ✗, 15.11 17:00 ✗, 18.11 17:00 ✗ | 0/3 | 0.0 h | 38.7 h | 20 | 0 of the next 3 slots have a video; last successful build 38.7 h ago |
| [Yesterday in Color](https://github.com/edbackulin-eng/archive-channel) | ✗ | 10.11 12:00 ✗, 13.11 12:00 ✗, 17.11 12:00 ✗ | 0/3 | 0.0 h | 2.5 h | 19 | 0 of the next 3 slots have a video; 1950s-suburb: qa-failed: repeats; thumbnail |
| [Stoic (yt-factory-daily)](https://github.com/beautyapp800-ctrl/yt-factory-daily) | ✓ | 09.11 21:00 ✓, 10.11 21:00 ✗, 11.11 21:00 ✗ | 1/3 | 5.9 h | 12.2 h | generates | — |

**Kaggle GPU, last 7 days:** 11.5 h of 27.5 h (closed-tabs 9.36 h, What If 0.0 h, dinosaurs 2.14 h).

## Journal (last 24 h)

| UTC | Channel | Level | Action | Why | Result |
|---|---|---|---|---|---|
| 11-09 05:01 | archive | 2 | autofix | prepare / run python automation "$slug" narrate | | no patch: the edit does not match the file once |
| 11-09 02:29 | archive | 2 | autofix | prepare / run python automation "$slug" narrate | | no patch: Gemini: The failure log is empty, so the error in the narrate step cannot be det |
| 11-09 02:29 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-09 02:29 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-08 23:25 | archive | 2 | autofix | prepare / run python automation "$slug" narrate | | no patch: Gemini: The error log is missing from the prompt. |
| 11-08 23:25 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-08 23:25 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-08 20:24 | archive | 2 | autofix | prepare / run python automation "$slug" narrate | | no patch: Gemini: The error text is missing from the prompt. |
| 11-08 20:24 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-08 20:24 | archive | 1 | start watchdog.yml | hung | started |
| 11-08 20:24 | archive | 1 | cancel watchdog.yml run 42484741975 | running 7.0 h (limit 6.2 h) | cancelled |
| 11-08 20:24 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-08 17:22 | archive | 2 | autofix | prepare / run python automation "$slug" narrate | | no patch: Gemini: No error log was provided to identify the cause of the failure in the na |
| 11-08 17:22 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-08 17:22 | dinosaurs | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-08 14:19 | archive | 2 | autofix | prepare / run python automation "$slug" narrate | | no patch: Gemini: No error log was provided to determine the cause of the failure. |
| 11-08 14:19 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-08 14:19 | dinosaurs | 1 | start episode.yml | 1 of the next 3 slots have a video | started |
| 11-08 11:18 | archive | 2 | autofix | prepare / run python automation "$slug" script | | no patch: Gemini: No error log was provided in the prompt to diagnose the exact failure. |
| 11-08 11:18 | dinosaurs | 2 | autofix | part (#) / render part # | | no patch: Gemini: The error log was omitted from the prompt, making it impossible to ident |
| 11-08 11:18 | dinosaurs | 1 | start episode.yml | 1 of the next 3 slots have a video | started |
| 11-08 08:11 | archive | 2 | autofix | prepare / run python automation "$slug" script | | no patch: Gemini: No failure log was provided to determine why the script step failed. |
| 11-08 08:11 | archive | 1 | start episode.yml | 0 of the next 3 slots have a video | started |
| 11-08 08:11 | dinosaurs | 2 | autofix | part (#) / render part # | | no patch: Gemini: The error log is empty, so the exact cause of the step failure cannot be |
| 11-08 08:11 | dinosaurs | 1 | start episode.yml | 1 of the next 3 slots have a video | started |
| 11-08 05:09 | archive | 2 | autofix | prepare / run python automation "$slug" script | | no patch: Gemini: No failure log was provided to diagnose why the script step failed. |
| 11-08 05:09 | dinosaurs | 2 | autofix | part (#) / render part # | | no patch: Gemini: The failure log is empty, making the exact cause of the failure in the ' |
