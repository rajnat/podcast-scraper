import os
import logging
from pyannote.audio import Pipeline

def diarize_audio(audio_path, hf_token):
    """
    Perform speaker diarization using Pyannote.
    """
    os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
    try:
        pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=hf_token)
        diarization = pipeline(audio_path)
        log.info(f"Finished diarizing audio file {audio_path}")
        return diarization
    except Exception as e:
        logging.exception(f"{e}")
        raise RuntimeError(f"Failed to diarize {audio_path}: {e}")
