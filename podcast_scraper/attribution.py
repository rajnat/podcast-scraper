import re

def assign_speaker_labels(transcript):
    host_name = "Russ Roberts"
    guest_name = None
    host_pattern = r"your host russ roberts"
    guest_pattern = r"my guest today is (.+?)"

    # Identify Host and Guest from patterns
    for segment in transcript:
        text = segment["text"].lower()
        
        # Identify host
        if re.search(host_pattern, text):
            segment["speaker"] = "Host"
        
        # Identify guest name
        match = re.search(guest_pattern, text)
        if match:
            guest_name = match.group(1).strip()
            segment["speaker"] = "Host"  # The host usually introduces the guest
            
    # Re-attribute Unknown speakers based on proximity and context
    for i, segment in enumerate(transcript):
        if segment["speaker"] == "Unknown":
            text = segment["text"].lower()
            
            # Guess speaker based on context
            if i > 0 and transcript[i - 1]["speaker"] == "Host":
                segment["speaker"] = "Guest"
            elif i > 0 and transcript[i - 1]["speaker"] == "Guest":
                segment["speaker"] = "Host"
            
    # Replace placeholder speaker names with 'Host' or 'Guest'
    for segment in transcript:
        if segment["speaker"] == "SPEAKER_00" or segment["speaker"] == "Host":
            segment["speaker"] = "Host"
        elif segment["speaker"] == "SPEAKER_01" or segment["speaker"] == "Guest":
            segment["speaker"] = "Guest"
        elif "russ" in segment["text"].lower():
            segment["speaker"] = "Host"
        elif guest_name and guest_name.lower() in segment["text"].lower():
            segment["speaker"] = "Guest"

    return transcript