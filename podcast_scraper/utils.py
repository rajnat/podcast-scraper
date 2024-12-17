import requests
import os
import logging
from bs4 import BeautifulSoup

def download_podcast(mp3_url, save_path):
    """Downloads the podcast from the given MP3 URL."""
    response = requests.get(mp3_url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        logging.info(f"Podcast downloaded successfully: {save_path}")
    else:
        logging.info(f"Failed to download podcast. Status code: {response.status_code}")

def save_transcript_to_file(transcript, output_file):
    """
    Save the transcript to a file in a readable format.
    
    :param transcript: List of dictionaries containing 'speaker', 'start', 'end', and 'text'.
    :param output_file: Path to the output file.
    """
    with open(output_file, "w", encoding="utf-8") as f:
        for segment in transcript:
            line = f"{segment['speaker']} ({segment['start']:.2f}-{segment['end']:.2f}): {segment['text']}\n"
            f.write(line)


def get_page_title(url):
    """
    Extract the title of the HTML page from the given URL.
    
    :param url: The URL of the webpage.
    :return: Cleaned title of the page.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract the title and sanitize it for filenames
    title = soup.title.string.strip()
    sanitized_title = title.replace(" ", "_").replace("/", "-").replace("\\", "-")  # Avoid invalid characters
    return sanitized_title
