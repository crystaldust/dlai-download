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

    # Wait for popup content to load and click the download button.
    # Video DownloadHelper uses nested shadow DOM:
    #   <vbox id="media">
    #     <com-media>         ← shadow host #1
    #       #shadow-root
    #         <com-media-discovered>  ← shadow host #2
    #           #shadow-root
    #             <button id="action_download">
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
        )
        # Give the extension popup time to populate its download list
        time.sleep(3)

        # Pierce through two levels of shadow DOM to reach the download button
        media_el = driver.find_element(By.CSS_SELECTOR, "com-media")
        shadow1 = media_el.shadow_root
        discovered_el = shadow1.find_element(By.CSS_SELECTOR, "com-media-discovered")
        shadow2 = discovered_el.shadow_root
        download_button = shadow2.find_element(By.CSS_SELECTOR, "#action_download")
        download_button.click()
        time.sleep(2)
    except Exception as e:
        print(f"  Warning: Extension popup interaction failed: {e}")

    # Navigate back to the original course page
    # driver.get(original_url)
    return original_url


def download_path(watch_dir, prefix, video_name):
    """Return the expected download file path for a video."""
    watch_dir = os.path.expanduser(watch_dir)
    expected_file = f"{prefix}__{sanitize_filename(video_name)}.mp4"
    return os.path.join(watch_dir, expected_file)


def wait_for_download(watch_dir, prefix, video_name, timeout=300):
    """Wait for {prefix}_{video_name}.mp4 to appear in watch_dir."""
    file_path = download_path(watch_dir, prefix, video_name)
    print(f'Checking if {file_path} exists')
    start_time = time.time()
    while time.time() - start_time < timeout:
        if os.path.exists(file_path):
            print(f"  Found: {file_path}")
            return file_path
        time.sleep(2)

    raise TimeoutError(
        f"{expected_file} did not appear in {watch_dir} within {timeout}s"
    )


def sanitize_filename(name):
    """Remove or replace characters that are invalid in filenames."""
    name = re.sub(r'[<>:"/\\|?*&,]', "", name)
    name = re.sub(r"\s+", " ", name)
    # return name.strip("_")
    return name


def dest_path(output_dir, index, lesson_title, ext=".mp4"):
    """Return the destination file path for a lesson."""
    safe_title = sanitize_filename(lesson_title)
    return os.path.join(output_dir, f"{index:02d}_{safe_title}{ext}")


def copy_to_output(src_path, output_dir, index, lesson_title):
    """Copy downloaded file to the output directory with a clean name."""
    os.makedirs(output_dir, exist_ok=True)
    ext = os.path.splitext(src_path)[1]
    dst = dest_path(output_dir, index, lesson_title, ext)
    shutil.copy2(src_path, dst)
    print(f"  Copied to: {dst}")
    return dst
