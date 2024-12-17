import logging
from podcast_scraper.attribution import assign_speaker_labels

def combine_transcription_and_diarization(transcription_segments, diarization):
    """
    Combine transcription and speaker diarization outputs into a cohesive transcript.
    :param transcription_segments: List of transcription segments with timestamps.
    :param diarization: Pyannote diarization output.
    :return: List of combined transcript entries with speaker attribution.
    """
    logging.info("Combining transcription with diarization...")
    # Validate transcription_segments
    if not isinstance(transcription_segments, list):
        raise TypeError("transcription_segments must be a list of dictionaries with 'start', 'end', and 'text' keys.")
    for i, seg in enumerate(transcription_segments):
        if not isinstance(seg, dict):
            raise TypeError(f"Segment at index {i} is not a dictionary: {seg}")
        if not all(k in seg for k in ("start", "end", "text")):
            raise ValueError(f"Segment at index {i} is missing required keys: {seg}")

    combined_transcript = []

    # Process each transcription segment
    for seg in transcription_segments:
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

        combined_transcript.append({
            "speaker": speaker_label,
            "start": seg_start,
            "end": seg_end,
            "text": text
        })

    # Log the final transcript
    attributed_transcript = assign_speaker_labels(combined_transcript)
    return attributed_transcript