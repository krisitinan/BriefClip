# BriefClip

BriefClip is a Streamlit app that takes a YouTube link, fetches the transcript, and turns it into a short study-friendly summary using Gemini.

## What It Does

- Accepts a YouTube video URL
- Extracts the transcript from the video
- Sends the transcript to Gemini for analysis
- Displays a study brief with:
  - The Bottom Line
  - Core Concepts
  - Study Notes
  - Action Item
- Optionally shows the full transcript

## Requirements

- Windows PowerShell
- Python installed at:
  `C:\Users\krisi\AppData\Local\Python\pythoncore-3.14-64\python.exe`
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

## Install Dependencies

Open PowerShell in the project folder:

```powershell
cd C:\Users\krisi\Desktop\BriefClip
& C:\Users\krisi\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pip install -r requirements.txt --upgrade
```

## Save Your API Key Once

To avoid typing your API key every time, create this file:

`C:\Users\krisi\Desktop\BriefClip\.streamlit\secrets.toml`

Add this content:

```toml
GEMINI_API_KEY = "your-gemini-api-key-here"
```

If the `.streamlit` folder does not exist, create it first.

The app will automatically use this key the next time it starts.

## Run The App

From the project folder, run:

```powershell
& C:\Users\krisi\AppData\Local\Python\pythoncore-3.14-64\python.exe -m streamlit run app.py
```

Streamlit will print a local URL in the terminal, usually:

```text
http://localhost:8501
```

Open that link in your browser.

## How To Use It

1. Start the app.
2. If you did not save your key in `secrets.toml`, paste your Gemini API key into the sidebar.
3. Paste a YouTube link into the input box.
4. Click `Generate Brief`.
5. Wait while the app:
   - fetches the transcript
   - analyzes the transcript with Gemini
6. Read the results in the `Summary` tab.
7. Open the `Transcript` tab if you enabled transcript display in the sidebar.

## Notes

- Some YouTube videos do not have captions, so transcript extraction may fail.
- Very long transcripts are trimmed before being sent to Gemini.
- If a model error appears, try a different model name in the sidebar.
- Your local secrets file is ignored by Git through `.gitignore`.

## Project Files

- `app.py` - main Streamlit app
- `requirements.txt` - Python dependencies
- `.streamlit/secrets.toml` - your local Gemini API key file
- `extraction.py` - transcript test/helper script

## Git Setup

To initialize Git for this project only:

```powershell
cd C:\Users\krisi\Desktop\BriefClip
git init
git add .
git commit -m "Initial commit"
```

## Troubleshooting

### Streamlit command not found

Run Streamlit through Python instead:

```powershell
& C:\Users\krisi\AppData\Local\Python\pythoncore-3.14-64\python.exe -m streamlit run app.py
```

### Secrets file error

If Streamlit says no secrets were found, either:

- create `.streamlit\secrets.toml`, or
- paste your Gemini API key into the sidebar when the app opens

### Gemini model not found

The selected model may not be available for your SDK or API key. Try changing the model name in the sidebar.

### Transcript fetch fails

Possible reasons:

- the video has no captions
- the link is invalid
- the transcript is restricted

## Security

- Do not hardcode API keys in Python files.
- Keep `secrets.toml` local only.
- If a key was ever exposed, revoke it and create a new one.
