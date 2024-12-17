from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import logging

def scrape_episode_links(page_url, xpath):
    """
    Scrapes all episode links from a webpage using a given XPath.
    :param page_url: URL of the webpage to scrape.
    :param xpath: XPath to locate episode links.
    :return: List of episode URLs.
    """
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    try:
        # Open the webpage
        driver.get(page_url)
        # Find all matching elements
        elements = driver.find_elements(By.XPATH, xpath)
        # Extract the href attribute from each element
        episode_links = [element.get_attribute("href") for element in elements]
        logging.info(f"Found {len(episode_links)} episode links.")
        return episode_links
    finally:
        driver.quit()

def scrape_mp3_url(driver, page_url, iframe_xpath, link_xpath):
    """
    Scrapes the MP3 URL from a webpage using Selenium.
    :param driver: Reused WebDriver instance.
    :param page_url: URL of the webpage to scrape.
    :param iframe_xpath: XPath to locate the iframe element containing the audio player.
    :param link_xpath: XPath to locate the direct MP3 download link.
    :return: Tuple of MP3 URLs (iframe_src, direct_mp3) if found, None otherwise.
    """
    try:
        driver.get(page_url)

        # Initialize results
        iframe_src = None
        direct_mp3 = None

        # Try to find the iframe source
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, iframe_xpath))
            )
            iframe_element = driver.find_element(By.XPATH, iframe_xpath)
            iframe_src = iframe_element.get_attribute("src")
            if iframe_src:
                logging.info(f"Iframe source found: {iframe_src}")
        except TimeoutException:
            logging.info(f"Timeout: No iframe element found on page: {page_url}. Continuing...")
        except NoSuchElementException:
            logging.info(f"No iframe element found on page: {page_url}. Continuing...")

        # Try to find the direct MP3 link
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, link_xpath))
            )
            link_element = driver.find_element(By.XPATH, link_xpath)
            direct_mp3 = link_element.get_attribute("href")
            if direct_mp3:
                logging.info(f"Direct MP3 link found: {direct_mp3}")
        except TimeoutException:
            logging.info(f"Timeout: No MP3 link found on page: {page_url}. Continuing...")
        except NoSuchElementException:
            logging.info(f"No MP3 link found on page: {page_url}. Continuing...")

        return iframe_src, direct_mp3

    except Exception as e:
        logging.info(f"Error while scraping URL: {page_url}. Error: {e}")
        return None, None
