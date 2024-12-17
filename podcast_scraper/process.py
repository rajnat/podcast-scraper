import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from podcast_scraper.scrape import scrape_mp3_url
from podcast_scraper.transcribe import generate_transcript
from podcast_scraper.utils import download_podcast, save_text


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

    semantic_data = []
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        for i, url in enumerate(urls):
            url = url.strip()
            print(f"Processing URL {i + 1}/{len(urls)}: {url}")

            # Scrape the MP3 URLs (iframe source and direct link)
            iframe_src, direct_mp3 = scrape_mp3_url(driver, url, iframe_xpath, element_xpath)
            
            if not iframe_src and not direct_mp3:
                print(f"No valid MP3 URL found for {url}. Skipping...")
                continue

            mp3_url = direct_mp3 or iframe_src
            if not mp3_url:
                print(f"No MP3 URL to process for {url}. Skipping...")
                continue

            audio_file = os.path.join(audio_dir, f"episode_{i + 1}.mp3")
            try:
                download_podcast(mp3_url, audio_file)
            except Exception as e:
                print(f"Failed to download audio from {mp3_url}. Skipping... Error: {e}")
                continue

            try:
                transcript = generate_transcript('data/output/audio/episode_1.mp3')
                transcript_file = os.path.join(transcripts_dir, f"episode_{i + 1}.txt")
                save_text(transcript_file, transcript)
            except Exception as e:
                print(f"Failed to transcribe audio file {audio_file}. Skipping... Error: {e}")
                continue

            semantic_data.append({
                "url": url,
                "iframe_src": iframe_src,
                "direct_mp3": direct_mp3,
                "used_mp3_url": mp3_url,
                "audio_file": audio_file,
                "transcript_file": transcript_file,
                "transcript_text": transcript
            })
    finally:
        driver.quit()

    semantic_data_file = os.path.join(output_dir, "semantic_data.json")
    with open(semantic_data_file, "w") as file:
        json.dump(semantic_data, file, indent=4)
    print(f"Semantic data saved: {semantic_data_file}")
