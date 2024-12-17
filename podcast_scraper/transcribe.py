from pyannote.audio import Pipeline
from pydub import AudioSegment
import whisper
import os
import re
import logging
import torch
from podcast_scraper.attribution import assign_speaker_labels

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
def initialize_pipeline():
    """
    Initialize the Pyannote pipeline and move models to the MPS device (GPU on Apple Silicon).
    """
    os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
    hf_token = os.getenv("HF_API_TOKEN")
    # Check MPS availability
    # if torch.backends.mps.is_available():
    #     torch.set_default_tensor_type(torch.FloatTensor)  # Ensure tensors default to float
    torch.set_default_device("cpu")  # Set MPS as the default device for PyTorch

    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=hf_token)
    
    return pipeline


def generate_transcript(audio_path):

    # Convert to wav to help with speech segmentation and encoding issues with mp3
    audio = AudioSegment.from_file(audio_path, format="mp3")
    wav_path = audio_path.replace('.mp3', '.wav')
    audio.export(wav_path, format="wav")

    """Transcribes the audio file using Whisper and performs speaker diarization."""
    logging.info(f"Starting transcription and speaker diarization for {wav_path}")


    # Load the Pyannote speaker diarization pipeline
    logging.info(f"Performing speaker diarization... for {wav_path}")
    pipeline = initialize_pipeline()
    diarization = pipeline(wav_path)

    # Load the Whisper model
    os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
    model = whisper.load_model("base").to("cpu")  # Use 'base' model (can be adjusted)

    # Transcribe with timestamps
    logging.info("Transcribing with Whisper...")
    result = model.transcribe(wav_path, word_timestamps=True)
    segments = result["segments"]  # Contains the timestamped text

    # Combine transcription with speaker diarization
    logging.info("Combining transcription with speaker diarization...")
    final_transcript = []

    for seg in segments:
        seg_start = seg["start"]
        seg_end = seg["end"]
        text = seg["text"]

        # Find the speaker for this segment based on overlap
        speaker_label = "Unknown"
        for speaker_segment in diarization.itertracks(yield_label=True):
            speaker_start = speaker_segment[0].start
            speaker_end = speaker_segment[0].end
            speaker = speaker_segment[2]

            # Check if transcription segment overlaps with speaker segment
            if seg_start >= speaker_start and seg_end <= speaker_end:
                speaker_label = speaker
                break

        final_transcript.append({
            "speaker": speaker_label,
            "start": seg_start,
            "end": seg_end,
            "text": text
        })

    # logging.info and return the combined results
    for line in final_transcript:
        logging.debug(f"Speaker {line['speaker']} ({line['start']:.2f}-{line['end']:.2f}): {line['text']}")

    attributed_transcript = assign_speaker_labels(final_transcript)
    return attributed_transcript