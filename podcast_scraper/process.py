import os
import json
import logging
import jsonlines
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from podcast_scraper.scrape import scrape_mp3_url
from podcast_scraper.transcribe import generate_transcript
from podcast_scraper.utils import download_podcast, save_transcript_to_file, get_page_title


def process_urls(file_path, iframe_xpath, element_xpath, output_dir):
    """
    Processes a list of podcast URLs to scrape, download, and transcribe audio files.
    :param file_path: Path to the file containing podcast URLs.
    :param iframe_xpath: XPath to locate the iframe element.
    :param element_xpath: XPath to locate the direct MP3 link.
    :param output_dir: Directory to store audio, transcripts, and metadata.
    """
    os.makedirs(output_dir, exist_ok=True)
    audio_dir = os.path.join(output_dir, "audio")
    transcripts_dir = os.path.join(output_dir, "transcripts")
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(transcripts_dir, exist_ok=True)

    with open(file_path, "r") as file:
        urls = file.readlines()

    semantic_data_file = os.path.join(output_dir, "semantic_data.jsonl")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        for i, url in enumerate(urls):
            url = url.strip()
            logging.info(f"Processing URL {i + 1}/{len(urls)}: {url}")

            # Scrape the MP3 URLs (iframe source and direct link)
            iframe_src, direct_mp3 = scrape_mp3_url(driver, url, iframe_xpath, element_xpath)
            
            if not iframe_src and not direct_mp3:
                logging.info(f"No valid MP3 URL found for {url}. Skipping...")
                continue

            mp3_url = direct_mp3 or iframe_src
            if not mp3_url:
                logging.info(f"No MP3 URL to process for {url}. Skipping...")
                continue
            title = get_page_title(url)
            audio_file = os.path.join(audio_dir, f"{title}.mp3")
            try:
                download_podcast(mp3_url, audio_file)
            except Exception as e:
                logging.info(f"Failed to download audio from {mp3_url}. Skipping... Error: {e}")
                continue

            try:
                transcript = generate_transcript(audio_file)
                transcript_file = os.path.join(transcripts_dir, f"{title}.txt")
                save_transcript_to_file(transcript, transcript_file)
            except Exception as e:
                logging.info(f"Failed to transcribe audio file {audio_file}. Skipping... Error: {e}")
                continue

                # Prepare data entry
                data_entry = {
                    "url": url,
                    "iframe_src": iframe_src,
                    "direct_mp3": direct_mp3,
                    "used_mp3_url": mp3_url,
                    "audio_file": audio_file,
                    "transcript_file": transcript_file,
                    "transcript_text": transcript
                }

                # Append to JSONL file
                with jsonlines.open(semantic_data_file, mode='a') as writer:
                    writer.write(data_entry)
                logging.info(f"Data appended for URL: {url}")
    finally:
        driver.quit()
