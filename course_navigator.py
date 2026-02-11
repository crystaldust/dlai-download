import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_lesson_list(driver):
    """Parse the sidebar and return a list of lesson dicts."""
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-testid^='lesson-item-']"))
    )

    lesson_elements = driver.find_elements(By.CSS_SELECTOR, "li[data-testid^='lesson-item-']")
    lessons = []

    for idx, li in enumerate(lesson_elements, start=1):
        # The <li> is inside an <a> tag
        parent_a = li.find_element(By.XPATH, "./..")
        href = parent_a.get_attribute("href") if parent_a.tag_name == "a" else ""

        title_el = li.find_element(By.CSS_SELECTOR, ".lesson-content .text-left")
        title = title_el.text.strip()

        type_el = li.find_element(By.CSS_SELECTOR, ".text-base-content-secondary")
        type_text = type_el.text.strip()

        testid = li.get_attribute("data-testid") or ""
        lesson_id = testid.replace("lesson-item-", "")

        lessons.append({
            "index": idx,
            "id": lesson_id,
            "title": title,
            "type_text": type_text,
            "url": href,
            "element": parent_a,
        })

    return lessons


def is_video_lesson(lesson):
    """Check if the lesson type contains 'Video'."""
    return "Video" in lesson["type_text"]


def click_lesson(driver, lesson, page_load_wait=10):
    """Click a sidebar lesson link and wait for the page to load."""
    lesson["element"].click()
    time.sleep(page_load_wait)
    # Wait for the video player or main content to be present
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".lesson-video-player, .lesson-content-area"))
        )
    except Exception:
        pass  # Some lessons may not have a video player
