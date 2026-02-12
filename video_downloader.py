import os
import re
import shutil
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def trigger_download(driver, config):
    """Open the Video DownloadHelper extension popup in the current tab and trigger a download."""
    browser = config.get("browser", "chrome").lower()
    if browser == "chrome":
        extension_id = config["chrome_extension_id"]
        popup_url = f"chrome-extension://{extension_id}/{config['extension_popup_path']}"
    else:
        extension_id = config["firefox_extension_id"]
        popup_url = f"moz-extension://{extension_id}/{config['extension_popup_path']}"

    # Remember the current page URL so we can navigate back
    original_url = driver.current_url

    # Navigate to extension popup in the same tab
    driver.get(popup_url)

    # Wait for popup content to load
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
        )
        # Give the extension popup time to populate its download list
        time.sleep(2)

        # Look for download links/buttons in the popup
        # Video DownloadHelper typically shows a list of detected media
        # Try common selectors for the download action
        # download_buttons = driver.find_elements(By.CSS_SELECTOR, ".download-btn, .action-btn, a[download], button")
        download_button = driver.find_elements(By.CSS_SELECTOR, "#action_download")
        if download_button:
            # Click the first available download option
            download_button.click()
            time.sleep(2)
    except Exception as e:
        print(f"  Warning: Extension popup interaction failed: {e}")

    # Navigate back to the original course page
    driver.get(original_url)


def wait_for_download(watch_dir, timeout=300):
    """Wait for a new file to appear in watch_dir and return its path once complete."""
    watch_dir = os.path.expanduser(watch_dir)

    # Snapshot existing files before download starts
    existing = set(os.listdir(watch_dir))

    start_time = time.time()
    new_file = None

    while time.time() - start_time < timeout:
        current = set(os.listdir(watch_dir))
        new_files = current - existing

        # Filter out temp/partial download files
        candidates = [
            f for f in new_files
            if not f.endswith((".crdownload", ".part", ".tmp", ".download"))
        ]

        if candidates:
            new_file = candidates[0]
            file_path = os.path.join(watch_dir, new_file)

            # Wait for file size to stabilize (download complete)
            prev_size = -1
            stable_count = 0
            while stable_count < 3:
                try:
                    curr_size = os.path.getsize(file_path)
                except OSError:
                    break
                if curr_size == prev_size:
                    stable_count += 1
                else:
                    stable_count = 0
                prev_size = curr_size
                time.sleep(1)

            return file_path

        time.sleep(2)

    raise TimeoutError(f"No new download appeared in {watch_dir} within {timeout}s")


def sanitize_filename(name):
    """Remove or replace characters that are invalid in filenames."""
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    name = re.sub(r"\s+", "_", name)
    return name.strip("_")


def copy_to_output(src_path, output_dir, index, lesson_title):
    """Copy downloaded file to the output directory with a clean name."""
    os.makedirs(output_dir, exist_ok=True)
    ext = os.path.splitext(src_path)[1]
    safe_title = sanitize_filename(lesson_title)
    dest_name = f"{index:02d}_{safe_title}{ext}"
    dest_path = os.path.join(output_dir, dest_name)
    shutil.copy2(src_path, dest_path)
    print(f"  Copied to: {dest_path}")
    return dest_path
