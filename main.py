from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import os
import requests, time
import io

# Optional: Read environment variable (defaults to "development")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

app = FastAPI(title="FastAPI Render Tutorial")

def generate_tts_bytes(text: str) -> bytes:
    url = "https://api.tts.quest/v3/voicevox/synthesis"
    response = requests.get(url, params={"text": text, "speaker": 54}).json()

    if not response.get("success"):
        raise Exception("VoiceVox request failed")

    status_url = response["audioStatusUrl"]
    mp3_url    = response["mp3DownloadUrl"]

    while True:
        status = requests.get(status_url).json()
        if status.get("isAudioReady"):
            break
        if status.get("isAudioError"):
            raise Exception("VoiceVox error generating audio")
        time.sleep(0.3)

    audio_file = requests.get(mp3_url)
    return audio_file.content

@app.get("/")
def read_root():
    return {
        "Hello": "World"
    }

@app.get("/tts")
def tts_endpoint(text: str = Query(..., description="Text to convert to speech")):
    audio_bytes = generate_tts_bytes(text)
    return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/mpeg", headers={
        "Content-Disposition": "attachment; filename=tts.mp3"
    })

