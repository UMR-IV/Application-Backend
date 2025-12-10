from fastapi import FastAPI
from pydantic import BaseModel
import requests, time, uuid, os

# Optional: Read environment variable (defaults to "development")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

app = FastAPI(title="FastAPI Render Tutorial")

@app.get("/")
def read_root():
    return {
        "Hello": "World"
    }


def generate_tts(text: str) -> str:
    os.makedirs("audio", exist_ok=True)
    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = os.path.join("audio", filename)

    url = "https://api.tts.quest/v3/voicevox/synthesis"

    response = requests.get(url, params={"text": text, "speaker": 54}).json()

    if not response.get("success"):
        raise Exception("VoiceVox request failed")

    # wait for audio
    status_url = response["audioStatusUrl"]
    mp3_url    = response["mp3DownloadUrl"]

    while True:
        status = requests.get(status_url).json()
        if status["isAudioReady"]:
            break
        if status["isAudioError"]:
            raise Exception("VoiceVox error generating audio")
        time.sleep(0.3)

    audio_file = requests.get(mp3_url)

    with open(filepath, "wb") as f:
        f.write(audio_file.content)

    return filename

# -----------------------------
# API Endpoint: /talk
# -----------------------------
class MessageRequest(BaseModel):
    message: str

@app.post("/talk")
async def process_message(req: MessageRequest):
    message = req.message
    print(f"🗣️ Received: {message}")
    print("Generating TTS...")
    mp3_file = generate_tts(message)
    print(os.path.basename(mp3_file))

    return {
        "message": message,
        "audio_url": f"https://fastapi-tutorial-wm71.onrender.com/get_audio/{os.path.basename(mp3_file)}"
    }