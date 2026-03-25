from youtube_transcript_api import YouTubeTranscriptApi
import re

def get_video_id(url):
    """
    Extracts the unique 11-character video ID from a YouTube URL.
    Handles standard, shortened (youtu.be), and mobile links.
    """
 
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def fetch_transcript(video_id):
    """
    Fetches the transcript text using the youtube-transcript-api.
    """
    try:

        transcript_data = YouTubeTranscriptApi().fetch(video_id)
        items = transcript_data.to_raw_data() if hasattr(transcript_data, "to_raw_data") else transcript_data

        full_text = " ".join(
            entry["text"] if isinstance(entry, dict) else getattr(entry, "text", "")
            for entry in items
        )
        return full_text
        
    except Exception as e:
        return f"Error: Could not retrieve transcript. {str(e)}"

# --- QUICK TEST ---
if __name__ == "__main__":
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 
    vid_id = get_video_id(test_url)
    
    if vid_id:
        print(f"Success! Video ID: {vid_id}")
        content = fetch_transcript(vid_id)
        print("\nFirst 300 characters of transcript:")
        print(content[:300])
    else:
        print("Invalid YouTube URL.")
