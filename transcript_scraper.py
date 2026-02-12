import os
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def open_transcript_panel(driver):
    """Click the 'Show Transcript' button to open the transcript panel."""
    try:
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[aria-label='Show transcript panel']")
            )
        )
        btn.click()
        # Wait for the transcript content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#panel-portal .flex-1.overflow-y-auto")
            )
        )
    except Exception as e:
        print(f"  Warning: Could not open transcript panel: {e}")
        raise


def scrape_transcript(driver):
    """Scrape transcript entries from the open transcript panel.

    Returns a list of (timestamp_str, text) tuples.
    """
    container = driver.find_element(
        By.CSS_SELECTOR, "#panel-portal .flex-1.overflow-y-auto"
    )
    entry_divs = container.find_elements(By.XPATH, "./div")

    entries = []
    for div in entry_divs:
        try:
            timestamp = div.find_element(By.CSS_SELECTOR, "button").text.strip()
            text = div.find_element(By.CSS_SELECTOR, "span").text.strip()
        except Exception:
            continue
        if timestamp and text:
            entries.append((timestamp, text))

    return entries


def parse_timestamp(ts_str):
    """Parse a timestamp string like '0:00' or '1:23:45' into total seconds."""
    parts = ts_str.split(":")
    parts = [int(p) for p in parts]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    elif len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    return 0


def seconds_to_srt_time(seconds):
    """Convert seconds to SRT timestamp format: HH:MM:SS,mmm"""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d},000"


def to_srt(entries):
    """Convert transcript entries to SRT subtitle format.

    Each entry is (timestamp_str, text). The end time is set to the start
    of the next entry, or start + 5 seconds for the last entry.
    """
    if not entries:
        return ""

    srt_lines = []
    for i, (ts, text) in enumerate(entries):
        if not ts:
            continue
        start_sec = parse_timestamp(ts)
        # End time = next entry's start, or +5s for the last
        if i + 1 < len(entries) and entries[i + 1][0]:
            end_sec = parse_timestamp(entries[i + 1][0])
        else:
            end_sec = start_sec + 5

        start_srt = seconds_to_srt_time(start_sec)
        end_srt = seconds_to_srt_time(end_sec)

        srt_lines.append(f"{i + 1}")
        srt_lines.append(f"{start_srt} --> {end_srt}")
        srt_lines.append(text)
        srt_lines.append("")

    return "\n".join(srt_lines)


def sanitize_filename(name):
    """Remove or replace characters that are invalid in filenames."""
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    name = re.sub(r"\s+", "_", name)
    return name.strip("_")


def save_srt(srt_content, output_dir, index, lesson_title):
    """Save SRT content to a file."""
    os.makedirs(output_dir, exist_ok=True)
    safe_title = sanitize_filename(lesson_title)
    filename = f"{index:02d}_{safe_title}.srt"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(srt_content)
    print(f"  Saved transcript: {filepath}")
    return filepath
