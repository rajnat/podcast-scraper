import requests
import os

def download_podcast(mp3_url, save_path):
    """Downloads the podcast from the given MP3 URL."""
    response = requests.get(mp3_url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        print(f"Podcast downloaded successfully: {save_path}")
    else:
        print(f"Failed to download podcast. Status code: {response.status_code}")

def save_text(file_path, text):
    """Saves the given text to a file."""
    with open(file_path, "w") as file:
        file.write(text)
    print(f"File saved: {file_path}")
