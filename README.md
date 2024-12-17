# Podcast Scraper and Transcription Tool

This project provides a complete pipeline for scraping podcast episode URLs, downloading the associated audio files, and generating transcripts using OpenAI Whisper. The generated outputs (audio files, transcripts, and metadata) are structured to support building a semantic search engine.

### Features

    * Scrape MP3 URLs: Extract podcast audio file URLs from a list of webpage URLs using Selenium and XPath.
    * Download Audio Files: Automatically download audio files to a local directory.
    * Generate Transcripts: Transcribe audio files into text using the OpenAI Whisper model.
    * Save Metadata: Store structured metadata (e.g., URL, transcript, file paths) in a JSON file for future processing.
    * Extensible Design: Modular components for scraping, transcription, and orchestration.

### Requirements:
    Python 3.7+
    Google Chrome browser (for Selenium)
    Whisper (installed via pip)

### Installation:
    1. Clone the repository: `git clone https://github.com/rajnat/podcast-scraper.git`
    2. `cd podcast-scraper`
    3. Setup a python virtual environment: `python3 -m venv venv` and ` source venv/bin/activate`
    4. Install dependencies: `pip install -r requirements.txt`
    5. Prepare input data in the data/episodes.txt

### Future Enhancements:

    * Error Handling:
        Retry logic for failed downloads or transcripts.
    * Parallel Processing:
        Speed up downloads and transcription using multiprocessing or asynchronous programming.
    * Semantic Search Engine:
        Use the semantic_data.json to generate embeddings and build a search engine using tools like FAISS or Weaviate.
    * Support RSS feeds