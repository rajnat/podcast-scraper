import feedparser
from datetime import datetime, timezone

def parse_rss_feed(feed_url, start_date=None, end_date=None):
    """
    Parse an RSS feed and filter episodes by date.
    
    :param feed_url: URL of the RSS feed.
    :param start_date: Filter episodes published after this date (inclusive).
    :param end_date: Filter episodes published before this date (inclusive).
    :return: List of filtered episodes with metadata.
    """
    feed = feedparser.parse(feed_url)
    episodes = []

    for entry in feed.entries:
        # Parse the publication date
        pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        
        # Apply date filtering
        if start_date and pub_date < start_date:
            continue
        if end_date and pub_date > end_date:
            continue
        
        # Extract relevant episode details
        episodes.append({
            "title": entry.title,
            "link": entry.link,
            "pub_date": pub_date,
            "audio_url": entry.enclosures[0].href if entry.enclosures else None,
        })

    return episodes
