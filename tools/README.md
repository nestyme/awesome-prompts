# Tools — the agent's toolbox

Universal, composable helper tools the agent calls **on demand** while running
the skills. Each tool is a standalone Python CLI with one job. They share one
contract so the agent can call any of them the same way and chain them together.

## The contract

- **Invoke**: `python3 tools/<name>.py [flags]` (run from repo root).
- **Input**: CLI flags, and/or a JSON payload via `--in <file>` or `--in -` (stdin). Piping works: one tool's `data` feeds the next tool's `--in -`.
- **Output**: exactly ONE JSON object on stdout — an envelope:
  - success → `{"ok": true,  "tool": "<name>", "data": <result>}`
  - error   → `{"ok": false, "tool": "<name>", "error": {"code","message",...}}`
- **Exit code**: `0` success · `1` handled error · `2` bad usage.
- **Logs**: progress goes to **stderr**, never stdout — so stdout stays parseable.
- **Field aliases**: collectors emit different key names (TikTokApi `playCount`, yt-dlp `view_count`, …). All tools normalize via `_common.normalize_video`, so any collector's output pipes into the analytics tools unchanged.
- **Missing deps/keys**: a tool that needs an uninstalled package or an env key returns a clean `missing_dependency` / `missing_env` error (never a traceback). Install from `tools/requirements.txt` as needed.

## Map

Legend: **offline** = no network/keys, runs anywhere · **net** = calls an API · **key** = needs an env secret · **node** = needs Node.js (Remotion).

### Collect — acquire raw data
| Tool | Type | One-liner | Key flags |
|---|---|---|---|
| [`tiktok_account.py`](tiktok_account.py) | net | Pull an account's recent videos + stats (+ top comments). TikTokApi → yt-dlp fallback. | `--handle --count --comments` |
| [`video_metadata.py`](video_metadata.py) | net | Universal single-URL metadata (TikTok/IG/YT). The always-works fallback. | `--url` / `--url-file` |

### Analyze — turn data into signal (offline core)
| Tool | Type | One-liner | Key flags |
|---|---|---|---|
| [`engagement.py`](engagement.py) ⭐ | offline | Video stats → engagement_score, save_rate, ratios, freshness/lifecycle, format-vs-creator-vs-paid attribution. | `--follower-count --account-median --top --now` |
| [`account_stats.py`](account_stats.py) | offline | Aggregate an account → median views, cadence, outliers, paid-amp/shadow signals, size bucket. | `--official-cadence-days` |
| [`decompose_video.py`](decompose_video.py) | net | Download + extract keyframes + thumb-stop frame + transcript, for 7-axis analysis. | `--url/--file --transcribe` |

### Trends
| Tool | Type | One-liner | Key flags |
|---|---|---|---|
| [`trending_sounds.py`](trending_sounds.py) | net | TikTok Creative Center trending sounds/hashtags by region + window. | `--kind --region --period` |

### Generate — the paid creative steps
| Tool | Type | One-liner | Key flags |
|---|---|---|---|
| [`gen_image.py`](gen_image.py) | net·key | Gemini text→image / image-edit (persona ref, cover bank). No baked text. | `--prompt --ref --out` |
| [`gen_video.py`](gen_video.py) | net·key | Kling (fal.ai) image→video clip. | `--image --prompt --duration` |
| [`caption_composite.py`](caption_composite.py) | offline | Composite caption text onto a photo with platform-safe margins (PIL). Free, re-renderable. | `--image --text --position --box` |
| [`render_video.py`](render_video.py) | net·node | Assemble the final 9:16 video: animated **hook (~3s) + app demo**, via Remotion. `--dry-run` to preview props. | `--demo --hook-text --hook-media --hook-seconds --out` |

### Distribute & QA
| Tool | Type | One-liner | Key flags |
|---|---|---|---|
| [`safe_zones.py`](safe_zones.py) | offline | Audit a creative vs Meta/TikTok safe zones, crop-survival, thumbnail readability. | `--image --text-boxes --target-ratio` |
| [`schedule_post.py`](schedule_post.py) | net·key | Schedule a carousel/video via Postiz, AI-disclosure on. **Defaults to `--dry-run`.** | `--list-channels --channel-id --when --live` |

## Env keys (only for `key` tools)
`GEMINI_API_KEY` (gen_image) · `FAL_KEY` (gen_video) · `POSTIZ_API_KEY` + optional `POSTIZ_BASE_URL` (schedule_post).

## Canonical chains

```bash
# 1) Collect → aggregate → per-video analytics (the trendwatch example)
python3 tools/tiktok_account.py --handle stylebudget --count 30 > acct.json
python3 tools/account_stats.py --in acct.json          # -> median, cadence, paid-amp signals
python3 tools/engagement.py --in acct.json \
    --follower-count 42000 --account-median 8000 --top 10   # -> ranked ideation-eligible videos

# 2) Manual fallback when scrapers are blocked
python3 tools/video_metadata.py --url-file urls.txt | python3 tools/engagement.py --in -

# 3) Decompose a winner for 7-axis analysis
python3 tools/decompose_video.py --url <URL> --out ./frames --transcribe

# 4) Produce a carousel slide (free) and QA it before scheduling
python3 tools/gen_image.py --prompt "$(cat prompt.txt)" --ref ref_mia.png --out cover.png
python3 tools/caption_composite.py --image cover.png --text "one blazer, 5 fits" --out slide_01.png
python3 tools/safe_zones.py --image slide_01.png
python3 tools/schedule_post.py --channel-id abc --when 2026-07-02T08:30:00 \
    --caption "$(cat caption.txt)" --media slide_01.png    # dry-run by default; add --live after the gate

# 5) Assemble a hook+demo video (Remotion) — first run auto-installs node deps
python3 tools/render_video.py --demo demo.mp4 --hook-text "your closet before vs after" \
    --hook-media cover.png --brand myapp --out final.mp4   # --dry-run to preview props first
```

> `render_video.py` needs **Node.js 18+** (it wraps the Remotion project in `tools/remotion/`).
> The first render runs `npm install` there once (Remotion + a headless Chromium).

## Adding a tool
Copy the pattern: `import _common as c`, `c.set_tool("name")`, parse args, do one
job, `c.emit(data)` on success / `c.fail(msg, code=...)` on error. Then add a row
to the map above. Keep it single-purpose and JSON-in/JSON-out so it composes.
