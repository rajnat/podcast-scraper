from podcast_scraper.scraper import scrape_mp3_url
import requests
import logging
import os

def download_mp3(mp3_url, save_path):
    """Downloads the podcast from the given MP3 URL."""
    response = requests.get(mp3_url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        logging.info(f"Podcast downloaded successfully: {save_path}")
    else:
        logging.info(f"Failed to download podcast. Status code: {response.status_code}")