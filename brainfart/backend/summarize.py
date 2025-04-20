import os
import sys
import openai
import json
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import OPENAI_API_KEY

client = openai.OpenAI(api_key=OPENAI_API_KEY)

TRANSCRIPT_DIR = os.path.join("data", "transcripts")
NOTES_DIR = os.path.join("data", "notes")
os.makedirs(NOTES_DIR, exist_ok=True)

def summarize_transcript(transcript_text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an insightful world‑class summarizer and creative visionary."},
                {"role": "user", "content": f"Summarize and analyze the following transcript:\n\n{transcript_text}"}
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "return_summary",
                        "description": "Summarized information about a voice note",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "Short, memorable headline"
                                },
                                "category": {
                                    "type": "string",
                                    "description": "A one-word category label (e.g., tech, health, philosophy)"
                                },
                                "summary": {
                                    "type": "string",
                                    "description": "One or two direct sentences stating the core message—no “speaker,”“transcript,” or other meta‑language"
                                },
                                "insights": {
                                    "type": "array",
                                    "items": { "type": "string" },
                                    "description": "Profound creative remarks and questions to spark curiosity"
                                }
                            },
                            "required": ["title", "category", "summary", "insights"]
                        }
                    }
                }
            ],
            tool_choice="auto"
        )

        args_str = response.choices[0].message.tool_calls[0].function.arguments
        return json.loads(args_str)

    except Exception as e:
        print(f"❌ Error summarizing transcript: {e}")
        return None

if __name__ == "__main__":
    summarize_all()
