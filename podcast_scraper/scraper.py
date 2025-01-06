from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
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
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        # Find all matching elements
        elements = driver.find_elements(By.XPATH, xpath)
        logging.info(f"Found!!! {len(elements)}")
        # Extract the href attribute from each element
        episode_links = [element.get_attribute("href") for element in elements]
        logging.info(f"Found {len(episode_links)} episode links.")
        return episode_links
    finally:
        driver.quit()

def scrape_mp3_url(driver, page_url, iframe_xpath, link_xpath, max_retries=3, wait_time=5):
    """
    Scrapes the MP3 URL from a webpage using Selenium with retry logic.
    :param driver: Reused WebDriver instance.
    :param page_url: URL of the webpage to scrape.
    :param iframe_xpath: XPath to locate the iframe element containing the audio player.
    :param link_xpath: XPath to locate the direct MP3 download link.
    :param max_retries: Maximum number of retries if the scraping fails.
    :param wait_time: Time to wait between retries in seconds.
    :return: Tuple of MP3 URLs (iframe_src, direct_mp3) if found, None otherwise.
    """
    attempt = 0
    while attempt < max_retries:
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
            # Log the error for this attempt
            logging.error(f"Attempt {attempt + 1} failed while scraping URL: {page_url}. Error: {e}")

            # Restart the WebDriver if the error seems like a selenium issue or a page load issue
            if isinstance(driver, webdriver.Chrome) or isinstance(driver, webdriver.Firefox):
                logging.info(f"Restarting WebDriver... Attempt {attempt + 1} of {max_retries}")
                driver.quit()
                driver = webdriver.Chrome()  # Or webdriver.Firefox(), depending on the browser
                # You may also want to add some wait time before retrying the next attempt
                time.sleep(wait_time)

        attempt += 1

    # If we exhausted all retries, log and return None
    logging.error(f"Failed to scrape after {max_retries} attempts: {page_url}")
    return None, None