# Render schedule of the account edbackulin-eng (owner 17.11)

GitHub runs at most **20 jobs at once** for the whole account. Every channel's render matrix has a
`max-parallel`, every build workflow a `concurrency` group (one build of a channel at a time), and the
heavy windows are spread over the day so that even the worst overlap stays under 20.

| Channel | Workflow (concurrency group) | Matrix cap | When it renders (UTC) | Kaggle GPU |
|---|---|---|---|---|
| What If | `build-v2.yml` (`video-build-v2`) | blender 6 | starts 05:00-12:00 (watchdog), FLUX 07:00-17:30 | 07:00-17:30 |
| Closed Tabs | `daily.yml` (its own group) | - (one job) | 20:00-02:00 | from 20:00 |
| Urzeit-Archiv | `episode.yml` + `render.yml` | render shards 6 | any time; paused until the new format is approved (gate) | in What If's and Closed Tabs' free hours |
| Yesterday in Color | `episode.yml` (`episode`) | cut 4 | any time, ~2-2.5 h a build | - |
| America Over Time | `video.yml` (`video-render`) | segments 6 | Sun + Thu 01:00 (render only, no upload - automation off) | - |
| Huge To Scale | `produce.yml` (`produce`) -> `trial-shorts.yml` | render 4, data/compose 2 | daily 17:00 (~2 h a ladder; only when < 2 episodes are ready); upload.yml 14:00, topics.yml Mon 12:00 (1 job each) | - |
| Stoic, Moo Toot | other account (beautyapp800-ctrl) | - | not counted here | - |

Worst case at once: What If 6 + Urzeit 6 + Yesterday in Color 4 + Huge To Scale 4 = 20 (America Over
Time renders at 01:00, when What If does not start and Closed Tabs uses one job).

Rules:
- a new matrix gets a `max-parallel` and is added here before it runs;
- Huge To Scale is on since 18.11 (owner): renders 17:00-~20:00 UTC, after What If's starts (05:00-12:00) and before
  America Over Time (Sun/Thu 01:00); America Over Time stays render-only until the owner switches it on;
- the Kaggle GPU (FLUX) belongs to What If 07:00-17:30 and to Closed Tabs from 20:00 UTC;
- the channels monitor (`monitor.yml`, every 3 h) mails the owner when a channel has fewer than two videos
  ahead (Stoic and Moo Toot: one, their owner-set rhythm) or a slot went by with no video.
