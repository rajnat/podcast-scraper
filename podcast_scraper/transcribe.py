from pyannote.audio import Pipeline
from pydub import AudioSegment
import whisper
import os
import re
import logging
import torch
from podcast_scraper.attribution import assign_speaker_labels


import whisper

def transcribe_audio(audio_path, model_name="base"):
    """
    Transcribe audio using Whisper and return the transcript.
    """
    try:
        model = whisper.load_model(model_name)
        result = model.transcribe(audio_path)
        return result["text"], result  # Return text and raw Whisper result
    except Exception as e:
        raise RuntimeError(f"Failed to transcribe {audio_path}: {e}")
