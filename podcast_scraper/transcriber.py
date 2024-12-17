from pyannote.audio import Pipeline
from pydub import AudioSegment
import whisper
import os
import re
import logging
import torch
from podcast_scraper.attribution import assign_speaker_labels

def transcribe_audio(audio_path, model_name="base"):
    """
    Transcribe audio using Whisper and return the transcript and segments.
    """
    try:
        model = whisper.load_model(model_name)
        result = model.transcribe(audio_path)
        logging.info(f"Succeeded in transcribing {audio_path}")

        # Extract segments with start, end, and text
        transcription_segments = [
            {"start": seg["start"], "end": seg["end"], "text": seg["text"]}
            for seg in result.get("segments", [])
        ]

        return result["text"], transcription_segments  # Return full text and processed segments
    except Exception as e:
        logging.exception(f"{e}")
        raise RuntimeError(f"Failed to transcribe {audio_path}: {e}")
