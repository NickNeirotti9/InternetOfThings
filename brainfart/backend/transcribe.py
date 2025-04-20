import os
import sys
import openai
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import OPENAI_API_KEY

client = openai.OpenAI(api_key=OPENAI_API_KEY)

RAW_AUDIO_DIR = os.path.join("data", "raw_audio")
TRANSCRIPT_DIR = os.path.join("data", "transcripts")

def transcribe_file(audio_path):
    try:
        with open(audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            return response.text
    except Exception as e:
        print(f"Error transcribing {audio_path}: {e}")
        return None

if __name__ == "__main__":
    transcribe_all()
