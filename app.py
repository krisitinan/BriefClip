import json
import os
import re
from urllib.error import URLError
from urllib.parse import quote_plus
from urllib.request import urlopen

import streamlit as st
from google import genai
from streamlit.errors import StreamlitSecretNotFoundError
from youtube_transcript_api import YouTubeTranscriptApi


st.set_page_config(page_title="BriefClip", page_icon=":scissors:", layout="wide")

YOUTUBE_ID_PATTERN = r"(?:v=|/|be/|embed/|shorts/)([0-9A-Za-z_-]{11})"
MAX_TRANSCRIPT_CHARS = 30000
DEFAULT_TRANSCRIPT_LANGUAGES = ["en", "en-US", "en-GB"]
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


def get_video_id(url: str) -> str | None:
    """Extract the 11-character YouTube video ID from common URL formats."""
    match = re.search(YOUTUBE_ID_PATTERN, url)
    return match.group(1) if match else None


def fetch_transcript_text(video_id: str) -> str:
    """Fetch transcript text across newer and older youtube-transcript-api versions."""
    api = YouTubeTranscriptApi()

    try:
        transcript_data = api.fetch(video_id, languages=DEFAULT_TRANSCRIPT_LANGUAGES)
    except TypeError:
        transcript_data = api.fetch(video_id)
    except Exception:
        transcript_data = api.fetch(video_id)

    items = transcript_data.to_raw_data() if hasattr(transcript_data, "to_raw_data") else transcript_data
    parts = []

    for entry in items:
        if isinstance(entry, dict):
            text = entry.get("text", "")
        else:
            text = getattr(entry, "text", "")
        if text:
            parts.append(text.strip())

    transcript_text = " ".join(parts).strip()
    if not transcript_text:
        raise ValueError("Transcript was empty.")

    return transcript_text


def get_video_title(video_url: str) -> str | None:
    """Fetch a YouTube title through the public oEmbed endpoint."""
    endpoint = "https://www.youtube.com/oembed?url={url}&format=json".format(
        url=quote_plus(video_url)
    )

    try:
        with urlopen(endpoint, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return None

    return payload.get("title")


def build_prompt(transcript_text: str) -> str:
    """Build the summarization prompt sent to Gemini."""
    return f"""
You are BriefClip, a study assistant for busy students.

Analyze the YouTube transcript below and return Markdown with these sections:
- **The Bottom Line**: exactly 2 sentences
- **Core Concepts**: 5 concise bullet points
- **Study Notes**: 1 short paragraph explaining the hardest idea simply
- **Action Item**: 1 practical next step for the viewer

Transcript:
{transcript_text}
""".strip()


def get_summary(transcript_text: str, api_key: str, model_name: str) -> str:
    """Generate an analysis from the transcript using Gemini."""
    prompt_text = transcript_text[:MAX_TRANSCRIPT_CHARS]
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model_name,
        contents=build_prompt(prompt_text),
    )

    if not getattr(response, "text", None):
        raise ValueError("Gemini returned an empty response.")

    return response.text


def get_api_key() -> str:
    """Read the Gemini key from Streamlit secrets, env vars, or the sidebar."""
    try:
        secret_key = st.secrets.get("GEMINI_API_KEY", "")
    except StreamlitSecretNotFoundError:
        secret_key = ""

    return (
        secret_key
        or os.getenv("GEMINI_API_KEY")
        or st.session_state.get("api_key_input", "").strip()
    )


st.markdown("<h1 style='text-align: center;'>BriefClip</h1>", unsafe_allow_html=True)
st.write("Paste a YouTube link to transcribe it and generate a study-friendly analysis.")

with st.sidebar:
    st.subheader("Settings")
    st.text_input(
        "Gemini API key",
        type="password",
        key="api_key_input",
        help="Leave this blank if you already set GEMINI_API_KEY in secrets or environment variables.",
    )
    model_name = st.text_input(
        "Gemini model",
        value=DEFAULT_GEMINI_MODEL,
        help="Change this if your API key does not have access to the default model.",
    ).strip() or DEFAULT_GEMINI_MODEL
    show_transcript = st.checkbox("Show full transcript", value=False)

video_url = st.text_input(
    "YouTube link",
    placeholder="https://www.youtube.com/watch?v=...",
)
generate_btn = st.button("Generate Brief", type="primary", use_container_width=True)

if generate_btn:
    if not video_url.strip():
        st.warning("Enter a YouTube link first.")
    else:
        api_key = get_api_key()
        if not api_key:
            st.error("Add a Gemini API key in the sidebar, Streamlit secrets, or GEMINI_API_KEY.")
            st.stop()

        video_id = get_video_id(video_url.strip())
        if not video_id:
            st.error("That does not look like a valid YouTube link.")
            st.stop()

        try:
            video_title = get_video_title(video_url.strip())

            with st.spinner("Fetching transcript..."):
                transcript_text = fetch_transcript_text(video_id)

            with st.spinner("Analyzing transcript..."):
                summary = get_summary(transcript_text, api_key, model_name)

            st.divider()
            if video_title:
                st.subheader(video_title)

            summary_tab, transcript_tab = st.tabs(["Summary", "Transcript"])

            with summary_tab:
                st.subheader("Study Brief")
                st.markdown(summary)

                if len(transcript_text) > MAX_TRANSCRIPT_CHARS:
                    st.info(
                        "The transcript was long, so only the first part was sent to Gemini for analysis."
                    )

            with transcript_tab:
                if show_transcript:
                    st.text_area(
                        "Transcript text",
                        transcript_text,
                        height=420,
                        label_visibility="collapsed",
                    )
                else:
                    st.info("Enable 'Show full transcript' in the sidebar to display it here.")

            st.success("Brief complete.")

        except Exception as exc:
            message = str(exc)
            st.error(f"Could not process this video: {message}")
            if "API_KEY" in message or "api key" in message.lower() or "permission" in message.lower():
                st.info("Check that the Gemini API key is valid, active, and copied without extra spaces.")
            elif "model" in message.lower() or "not found" in message.lower():
                st.info("The selected Gemini model may not be available for this key. Try a different model name in the sidebar.")

st.divider()
st.caption("Built with Python, Streamlit, youtube-transcript-api, and Gemini.")
