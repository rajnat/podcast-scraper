from podcast_scraper.scrape import scrape_mp3_url
import requests
import logging
import os

def download_mp3(driver, page_url, iframe_xpath, link_xpath, output_dir):
    """
    Scrape and download an MP3 file from the given webpage.
    :param driver: Selenium WebDriver instance.
    :param page_url: URL of the webpage to scrape.
    :param iframe_xpath: XPath to locate iframe with the audio player.
    :param link_xpath: XPath to locate direct MP3 link.
    :param output_dir: Directory to save the MP3 file.
    :return: Path to the downloaded MP3 file.
    """
    try:
        iframe_src, mp3_url = scrape_mp3_url(driver, page_url, iframe_xpath, link_xpath)
        if not mp3_url:
            raise RuntimeError(f"No MP3 URL found on page: {page_url}")

        filename = os.path.join(output_dir, os.path.basename(mp3_url))
        response = requests.get(mp3_url, stream=True)
        response.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        logging.info(f"Downloaded MP3: {filename}")
        return filename
    except Exception as e:
        logging.error(f"Failed to download MP3 from {page_url}: {e}")
        raise