import os
import asyncio
import aiohttp
import logging
import jsonlines
from selenium import webdriver
from pydub import AudioSegment
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from podcast_scraper.scraper import scrape_mp3_url
from podcast_scraper.downloader import download_mp3
from podcast_scraper.transcriber import transcribe_audio
from podcast_scraper.diarizer import diarize_audio
from podcast_scraper.combiner import combine_transcription_and_diarization
from podcast_scraper.utils import get_page_title

async def process_file(file_path, iframe_xpath, link_xpath, output_dir, hf_token):
    """
    Processes episodes from a file containing URLs: scrape, download, transcribe, and diarize.
    
    :param file_path: Path to the file containing URLs.
    :param iframe_xpath: XPath to locate the iframe element.
    :param link_xpath: XPath to locate the direct MP3 link.
    :param output_dir: Directory to save results.
    :param hf_token: Hugging Face token for Pyannote diarization.
    """
    audio_dir = os.path.join(output_dir, "audio")
    transcripts_dir = os.path.join(output_dir, "transcripts")
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(transcripts_dir, exist_ok=True)

    with open(file_path, "r") as file:
        urls = [line.strip() for line in file.readlines()]

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    semantic_data_file = os.path.join(output_dir, "semantic_data.jsonl")

    async with aiohttp.ClientSession() as session:
        for url in urls:
            try:
                # Scrape MP3 URL
                iframe_src, direct_mp3 = scrape_mp3_url(driver, url, iframe_xpath, link_xpath)
                mp3_url = direct_mp3 or iframe_src
                if not mp3_url:
                    logging.info(f"No valid MP3 URL found for {url}. Skipping...")
                    continue

                # Download MP3
                file_name = get_page_title(url)
                mp3_path = os.path.join(audio_dir, f"{file_name}.mp3")
                download_mp3(mp3_url, mp3_path)

                # Convert to wav to help with speech segmentation and encoding issues with mp3
                audio = AudioSegment.from_file(mp3_path, format="mp3")
                audio_file = mp3_path.replace('.mp3', '.wav')
                audio.export(audio_file, format="wav")
                
                # Transcribe and diarize
                transcript_text, transcription_segments = transcribe_audio(audio_file)
                diarization_result = diarize_audio(audio_file, hf_token)
                combined_transcript = combine_transcription_and_diarization(transcription_segments, diarization_result)

                # Save combined transcript
                combined_file = os.path.join(transcripts_dir, f"{file_name}_combined.txt")
                with open(combined_file, "w") as f:
                    for entry in combined_transcript:
                        # Format each line with the updated speaker label and text
                        speaker = entry.get("speaker", "Unknown")
                        start = entry.get("start", 0)
                        end = entry.get("end", 0)
                        text = entry.get("text", "")
                        # Write the formatted line
                        f.write(f"Speaker {speaker} ({start:.2f}-{end:.2f}): {text}\n")
                logging.info(f"Processed and saved transcript for {url}.")

                #save the translated info in semantic_data.json
                data_entry = {
                    "url": url,
                    "iframe_src": iframe_src,
                    "direct_mp3": direct_mp3,
                    "used_mp3_url": mp3_url,
                    "audio_file": audio_file,
                    "transcript_file": combined_file,
                }

                # Append to JSONL file
                with jsonlines.open(semantic_data_file, mode='a') as writer:
                    writer.write(data_entry)
                logging.info(f"Data appended for URL: {url}")

            except Exception as e:
                logging.exception(f"Failed to process {url}: {e}")
    driver.quit()
