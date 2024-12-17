from pyannote.audio import Pipeline
from pydub import AudioSegment
import whisper
import os
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

def generate_transcript(audio_path):

    # Convert to wav to help with speech segmentation and encoding issues with mp3
    audio = AudioSegment.from_file(audio_path, format="mp3")
    wav_path = audio_path.replace('.mp3', '.wav')
    audio.export(wav_path, format="wav")

    """Transcribes the audio file using Whisper and performs speaker diarization."""
    print(f"Starting transcription and speaker diarization for {wav_path}")


    # Load the Pyannote speaker diarization pipeline
    print(f"Performing speaker diarization... for {wav_path}")
    hf_token = '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' #os.getenv("HF_API_TOKEN")  # Replace with your Hugging Face token
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=hf_token)
    diarization = pipeline(wav_path)

    # Load the Whisper model
    model = whisper.load_model("base")#.to("mps")  # Use 'base' model (can be adjusted)

    # Transcribe with timestamps
    print("Transcribing with Whisper...")
    result = model.transcribe(wav_path, word_timestamps=True)
    segments = result["segments"]  # Contains the timestamped text

    # Combine transcription with speaker diarization
    print("Combining transcription with speaker diarization...")
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

    # Print and return the combined results
    for line in final_transcript:
        print(f"Speaker {line['speaker']} ({line['start']:.2f}-{line['end']:.2f}): {line['text']}")

    return final_transcript