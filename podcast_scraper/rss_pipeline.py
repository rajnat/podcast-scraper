import os
import aiohttp
import logging
from podcast_scraper.downloader import download_mp3
from podcast_scraper.transcriber import transcribe_audio
from podcast_scraper.diarizer import diarize_audio
from podcast_scraper.combiner import combine_transcription_and_diarization
from podcast_scraper.rss_parser import parse_rss_feed


async def process_rss_feed(feed_url, output_dir, hf_token, start_date=None, end_date=None):
    """
    Processes episodes from an RSS feed: download, transcribe, and diarize.
    
    :param feed_url: URL of the RSS feed.
    :param output_dir: Directory to save results.
    :param hf_token: Hugging Face token for Pyannote diarization.
    :param start_date: Filter RSS episodes published after this date.
    :param end_date: Filter RSS episodes published before this date.
    """
    audio_dir = os.path.join(output_dir, "audio")
    transcripts_dir = os.path.join(output_dir, "transcripts")
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(transcripts_dir, exist_ok=True)

    # Parse the RSS feed
    episodes = parse_rss_feed(feed_url, start_date=start_date, end_date=end_date)
    logging.info(f"Found {len(episodes)} episodes to process.")

    async with aiohttp.ClientSession() as session:
        for episode in episodes:
            title = episode["title"]
            audio_url = episode["audio_url"]
            pub_date = episode["pub_date"]

            if not audio_url:
                logging.info(f"Skipping episode '{title}' (no audio URL found).")
                continue

            logging.info(f"Processing episode '{title}' published on {pub_date}.")

            try:
                # Download MP3
                audio_file = os.path.join(audio_dir, f"{title}.mp3")
                await download_mp3(audio_url, audio_file)

                # Transcribe and diarize
                transcript_text, transcription_segments = transcribe_audio(audio_file)
                diarization_result = diarize_audio(audio_file, hf_token)
                combined_transcript = combine_transcription_and_diarization(transcription_segments, diarization_result)

                # Save combined transcript
                combined_file = os.path.join(transcripts_dir, f"{os.path.basename(audio_file)}_combined.txt")
                with open(combined_file, "w") as f:
                    for entry in combined_transcript:
                        # Format each line with the updated speaker label and text
                        speaker = entry.get("speaker", "Unknown")
                        start = entry.get("start", 0)
                        end = entry.get("end", 0)
                        text = entry.get("text", "")
                        # Write the formatted line
                        f.write(f"Speaker {speaker} ({start:.2f}-{end:.2f}): {text}\n")
                logging.info(f"Saved transcript for episode '{title}'.")

            except Exception as e:
                logging.info(f"Failed to process episode '{title}': {e}")
