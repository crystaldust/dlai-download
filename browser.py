import re
import subprocess

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def _get_chrome_version(binary_path):
    """Get the major version number from a Chrome binary."""
    result = subprocess.run(
        [binary_path, "--version"],
        capture_output=True, text=True,
    )
    match = re.search(r"(\d+)\.\d+\.\d+", result.stdout)
    if not match:
        raise RuntimeError(f"Could not parse Chrome version from: {result.stdout.strip()}")
    return int(match.group(1))


def _get_chromedriver_version(driver_path):
    """Get the major version number from a chromedriver binary."""
    result = subprocess.run(
        [driver_path, "--version"],
        capture_output=True, text=True,
    )
    match = re.search(r"(\d+)\.\d+\.\d+", result.stdout)
    if not match:
        raise RuntimeError(f"Could not parse chromedriver version from: {result.stdout.strip()}")
    return int(match.group(1))


def _check_version_compatibility(config):
    """Verify that Chrome binary and chromedriver major versions match."""
    chrome_path = config.get("chrome_binary_path")
    driver_path = config.get("chromedriver_path")

    if not chrome_path or not driver_path:
        return  # Let Selenium handle auto-detection

    chrome_ver = _get_chrome_version(chrome_path)
    driver_ver = _get_chromedriver_version(driver_path)

    if chrome_ver != driver_ver:
        raise RuntimeError(
            f"Chrome/chromedriver version mismatch: "
            f"Chrome {chrome_ver} vs chromedriver {driver_ver}. "
            f"Both must share the same major version."
        )


def setup_browser(config):
    """Create a Chrome WebDriver using an existing user profile (with session/cookies)."""
    _check_version_compatibility(config)

    options = Options()
    options.add_argument(f"--user-data-dir={config['chrome_profile_path']}")
    # Disable the "Chrome is being controlled by automated software" bar
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    # Keep the browser open if the script crashes
    options.add_experimental_option("detach", True)

    if config.get("chrome_binary_path"):
        options.binary_location = config["chrome_binary_path"]

    service = None
    if config.get("chromedriver_path"):
        service = Service(executable_path=config["chromedriver_path"])

    driver = webdriver.Chrome(options=options, service=service or Service())
    driver.implicitly_wait(5)
    return driver
