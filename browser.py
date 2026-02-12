import re
import subprocess

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService


def _get_binary_version(binary_path):
    """Get the major version number from a browser/driver binary."""
    result = subprocess.run(
        [binary_path, "--version"],
        capture_output=True, text=True,
    )
    match = re.search(r"(\d+)\.\d+\.\d+", result.stdout)
    if not match:
        raise RuntimeError(f"Could not parse version from: {result.stdout.strip()}")
    return int(match.group(1))


def _check_version_compatibility(binary_path, driver_path):
    """Verify that browser and driver major versions match."""
    if not binary_path or not driver_path:
        return
    browser_ver = _get_binary_version(binary_path)
    driver_ver = _get_binary_version(driver_path)
    if browser_ver != driver_ver:
        raise RuntimeError(
            f"Browser/driver version mismatch: "
            f"browser {browser_ver} vs driver {driver_ver}. "
            f"Both must share the same major version."
        )


def _setup_chrome(config):
    """Set up a Chrome WebDriver."""
    _check_version_compatibility(
        config.get("chrome_binary_path"),
        config.get("chromedriver_path"),
    )

    options = ChromeOptions()
    options.add_argument(f"--user-data-dir={config['chrome_user_data_dir']}")
    options.add_argument(f"--profile-directory={config.get('chrome_profile_dir', 'Default')}")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--no-sandbox")
    options.add_experimental_option("detach", True)

    if config.get("chrome_binary_path"):
        options.binary_location = config["chrome_binary_path"]

    service = ChromeService()
    if config.get("chromedriver_path"):
        service = ChromeService(executable_path=config["chromedriver_path"])

    return webdriver.Chrome(options=options, service=service)


def _setup_firefox(config):
    """Set up a Firefox WebDriver."""
    _check_version_compatibility(
        config.get("firefox_binary_path"),
        config.get("geckodriver_path"),
    )

    options = FirefoxOptions()
    if config.get("firefox_profile_path"):
        options.profile = config["firefox_profile_path"]
    if config.get("firefox_binary_path"):
        options.binary_location = config["firefox_binary_path"]

    service = FirefoxService()
    if config.get("geckodriver_path"):
        service = FirefoxService(executable_path=config["geckodriver_path"])

    return webdriver.Firefox(options=options, service=service)


def setup_browser(config):
    """Create a WebDriver based on the configured browser type."""
    browser = config.get("browser", "chrome").lower()

    if browser == "chrome":
        driver = _setup_chrome(config)
    elif browser == "firefox":
        driver = _setup_firefox(config)
    else:
        raise ValueError(f"Unsupported browser: {browser}. Use 'chrome' or 'firefox'.")

    driver.implicitly_wait(5)
    return driver
