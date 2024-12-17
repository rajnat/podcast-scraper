import logging
import warnings
from podcast_scraper.scraper import scrape_episode_links
import argparse
from datetime import datetime, timezone
import asyncio
from podcast_scraper.rss_pipeline import process_rss_feed
from podcast_scraper.file_pipeline import process_file



def setup_logging():
    """
    Sets up logging with detailed format including line number and file name.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        handlers=[
            logging.StreamHandler(),  # Log to console
            logging.FileHandler("pipeline.log", mode="w"),  # Log to file
        ],
    )

def parse_args():
    parser = argparse.ArgumentParser(description="Podcast Processing Pipeline")
    parser.add_argument("--source", required=True, help="RSS feed URL or file path containing episode URLs.")
    parser.add_argument("--type", required=True, choices=["rss", "file"], help="Type of the source: 'rss' or 'file'.")
    parser.add_argument("--output-dir", default="data/output", help="Directory to save output files.")
    parser.add_argument("--iframe-xpath", help="XPath for iframe (required for 'file').")
    parser.add_argument("--link-xpath", help="XPath for MP3 link (required for 'file').")
    parser.add_argument("--hf-token", required=True, help="Hugging Face token for Pyannote diarization.")
    parser.add_argument("--start-date", help="Filter RSS episodes published after this date (YYYY-MM-DD).")
    parser.add_argument("--end-date", help="Filter RSS episodes published before this date (YYYY-MM-DD).")
    return parser.parse_args()


if __name__ == "__main__":
    setup_logging()
    args = parse_args()

    start_date = datetime.fromisoformat(args.start_date).replace(tzinfo=timezone.utc) if args.start_date else None
    end_date = datetime.fromisoformat(args.end_date).replace(tzinfo=timezone.utc) if args.end_date else None

    if args.type == "rss":
        asyncio.run(process_rss_feed(args.source, args.output_dir, args.hf_token, start_date, end_date))
    elif args.type == "file":
        if not args.iframe_xpath or not args.link_xpath:
            raise ValueError("Both --iframe-xpath and --link-xpath are required for 'file' type.")
        asyncio.run(process_file(args.source, args.iframe_xpath, args.link_xpath, args.output_dir, args.hf_token))

# # Example usage
# if __name__ == "__main__":
#     setup_logging()
#     page_url = "https://www.econlib.org/econtalk-archives-by-date/?selected_year=2007#content"  # Replace with the actual webpage URL
#     xpath = "/html/body/section[2]/div/div/article/div[2]/h3/a"
#     episode_links = scrape_episode_links(page_url, xpath)
#     logging.info(episode_links)