from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def setup_browser(config):
    """Create a Chrome WebDriver using an existing user profile (with session/cookies)."""
    options = Options()
    options.add_argument(f"--user-data-dir={config['chrome_profile_path']}")
    # Disable the "Chrome is being controlled by automated software" bar
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    # Keep the browser open if the script crashes
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    return driver
