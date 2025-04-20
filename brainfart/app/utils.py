import os
import glob
import json
import re
from datetime import datetime

def get_all_notes(): #Reads json files, parses info, sorts by date, returns list of dicts.
    notes = []
    for fn in glob.glob(os.path.join("data", "notes", "*.json")):
        with open(fn, "r") as f:
            note = json.load(f)
        notes.append({
            "filename": os.path.basename(fn),
            "title":    note.get("title", ""),
            "summary":  note.get("summary", ""),
            "date":     note.get("date", ""),
            "category": note.get("category", "")
        })
    notes.sort(key=lambda n: n["date"], reverse=True) # sort newest first
    return notes

def load_note(note_id): #Loads requested note by filename (note_id), returns parsed json.
    path = os.path.join("data", "notes", note_id)
    with open(path, "r") as f:
        return json.load(f)

def sorted_audio(path): #Gets audio files in a path, sorts by time, returns filenames
    entries = []
    for fn in os.listdir(path):
        if fn.lower().endswith((".mp3", ".wav", ".m4a")):
            full = os.path.join(path, fn)
            entries.append((fn, os.path.getmtime(full)))
    entries.sort(key=lambda x: x[1], reverse=True)
    return [fn for fn, _ in entries]

def get_all_transcripts(): #list of transcripts
    transcript_dir = os.path.join("data", "transcripts")
    paths = glob.glob(os.path.join(transcript_dir, "*.txt"))
    paths.sort(key=lambda p: os.path.getmtime(p), reverse=True) # sort by file mod. time

    transcripts = []
    for path in paths:
        with open(path, "r") as f:
            text = f.read().strip()
        transcripts.append({
            "filename": os.path.basename(path),
            "text": text
        })
    return transcripts

def date_from_filename(base_name: str) -> str: #filename like '20250416222104'to 'YYYY-MM-DD'
    m = re.match(r"^(\d{4})[_-]?(\d{2})[_-]?(\d{2})", base_name)
    if m:
        y, mo, da = m.groups()
        return f"{y}-{mo}-{da}"
    return datetime.now().strftime("%Y-%m-%d")
