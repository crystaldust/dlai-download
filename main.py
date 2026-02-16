import os

import yaml

from browser import setup_browser
from course_navigator import get_lesson_list, is_video_lesson, click_lesson
from transcript_scraper import open_transcript_panel, scrape_transcript, to_srt, save_srt, srt_output_path
from video_downloader import trigger_download, wait_for_download, copy_to_output, dest_path


def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def main():
    config = load_config()
    print("Starting browser...")
    driver = setup_browser(config)

    print(f"Navigating to course: {config['course_url']}")
    driver.get(config["course_url"])

    print("Parsing lesson list...")
    lessons = get_lesson_list(driver)
    print(f"Found {len(lessons)} lessons:")
    for lesson in lessons:
        marker = "[Video]" if is_video_lesson(lesson) else "[Skip] "
        print(f"  {lesson['index']:2d}. {marker} {lesson['title']}")

    for lesson in lessons:
        if not is_video_lesson(lesson):
            print(f"\nSkipping non-video: {lesson['index']}. {lesson['title']}")
            continue

        print(f"\nProcessing: {lesson['index']}. {lesson['title']}")
        if os.path.exists(dest_path(config["output_dir"], lesson["index"], lesson["title"])):
            print("  Already downloaded, skipping")
        else:
            click_lesson(driver, lesson, config.get("page_load_wait", 10))

            # Download video via extension
            print("  Triggering download via extension...")
            original_url = trigger_download(driver, config)
            print("  Waiting for download to complete...")
            downloaded_file = wait_for_download(
                config["download_watch_dir"],
                config["download_file_prefix"],
                lesson["title"],
                config.get("download_timeout", 300),
            )
            copy_to_output(downloaded_file, config["output_dir"], lesson["index"], lesson["title"])
            driver.get(original_url)

        # Scrape transcript
        if os.path.exists(srt_output_path(config["output_dir"], lesson["index"], lesson["title"])):
            print("  Subtitle already exists, skipping")
            continue

        print("  Scraping transcript...")
        try:
            open_transcript_panel(driver)
            entries = scrape_transcript(driver)
            if entries:
                srt_content = to_srt(entries)
                save_srt(srt_content, config["output_dir"], lesson["index"], lesson["title"])
            else:
                print("  Warning: No transcript entries found")
        except Exception as e:
            print(f"  Warning: Transcript scraping failed: {e}")

        print(f"  Done: {lesson['index']}. {lesson['title']}")

    print("\nAll lessons processed. Closing browser.")
    driver.quit()


if __name__ == "__main__":
    main()
