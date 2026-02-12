# DLAI Video Downloader

Selenium-based crawler to download DeepLearning.AI course videos using the Video DownloadHelper browser extension, and scrape transcripts into SRT subtitle files.

## Project Structure

```
main.py                  # Entry point - orchestrates full workflow
browser.py               # Browser setup (Chrome or Firefox) with user profile
course_navigator.py      # Sidebar parsing, lesson iteration, click navigation
video_downloader.py      # Extension popup interaction, file monitoring, copy
transcript_scraper.py    # Open transcript panel, scrape timestamps+text, save SRT
config.yaml              # All configuration (browser, paths, extension IDs)
dlai_sample_page.html    # Reference HTML for DLAI course page DOM structure
downloads/               # Output directory for videos + subtitles
```

## How to Run

```
uv run python main.py
```

Dependencies: `selenium`, `pyyaml` (managed by uv via `pyproject.toml`).

## Configuration (`config.yaml`)

- `browser`: `"chrome"` or `"firefox"`
- Chrome needs `chrome_user_data_dir` + `chrome_profile_dir` (default: `"Default"`)
- Firefox needs `firefox_profile_path`
- Binary and driver paths are all optional (Selenium auto-detects if empty)
- Extension IDs are separate per browser: `chrome_extension_id`, `firefox_extension_id`
- `extension_popup_path`: path within the extension package (e.g. `content/popup.html`)

## Key CSS Selectors (from dlai_sample_page.html)

| Element              | Selector                                          |
|----------------------|---------------------------------------------------|
| Sidebar lesson items | `li[data-testid^='lesson-item-']`                 |
| Lesson title         | `.lesson-content .text-left`                      |
| Lesson type/duration | `.text-base-content-secondary`                    |
| Video player         | `.lesson-video-player[data-media-player]`         |
| Transcript button    | `button[aria-label='Show transcript panel']`      |
| Extension download   | `#action_download`                                |

## Known Issues / TODO

- **Extension popup approach**: Navigating to the extension popup URL (`chrome-extension://` or `moz-extension://`) in the current tab loses the video page context, so the extension may not see downloadable media. A better approach would be to use a keyboard shortcut assigned to the extension (opens as real overlay popup while staying on the page). This would require adding an `extension_shortcut` config field and using `ActionChains` to send the key combo.
- **Transcript scraper**: The transcript panel DOM is dynamically loaded and not captured in the saved HTML. The scraper uses flexible/fallback selectors but may need tuning against the live site.
- **Download button selector**: Currently uses `#action_download` for Video DownloadHelper — may need adjustment depending on extension version.
