from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService


def _setup_chrome(config):
    """Set up a Chrome WebDriver."""
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

    driver.implicitly_wait(2)
    return driver
