from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import os
import json
import subprocess
import glob
from datetime import datetime
from .utils import get_all_notes, load_note, sorted_audio, get_all_transcripts, date_from_filename
from backend.transcribe import transcribe_file
from backend.summarize import summarize_transcript


main = Blueprint('main', __name__)

@main.route('/')
def home():
    all_audio = sorted_audio('data/raw_audio') #get all audio by date
    notes_dir = os.path.join('data','notes') #filter out audio already summarized by looking for filename in notes
    audio_files = [
        f for f in all_audio
        if not os.path.exists(
            os.path.join(notes_dir, os.path.splitext(f)[0] + '.json')
        )
    ]
    notes = get_all_notes()[:5] #displays the last 5 notes
    return render_template('home.html',audio_files=audio_files,notes=notes)

@main.route('/browse')
def browse():
    notes = get_all_notes()
    return render_template('browse.html', notes=notes)

@main.route('/note/<note_id>')
def note(note_id):
    note = load_note(note_id)
    return render_template('post.html', note=note)

@main.route("/sync", methods=["POST"])
def sync_audio():
    proc = subprocess.run(["python3", "backend/sync_audio.py"],check=True,capture_output=True,text=True)
    out = proc.stdout.strip()

    if out == "NO_DEVICE":
        flash("No device detected. Please connect your recorder.")
    elif out == "NO_NEW_AUDIO":
        flash("No new audio files to summarize.")
    elif out.startswith("NEW_AUDIO:"):
        files = out.split(":",1)[1].split(",")
        flash(f"✅ Synced {len(files)} new audio file(s): {', '.join(files)}")
    else:
        flash("Unexpected response: " + out)

    return redirect(url_for("main.home"))

@main.route('/audio/manage') #get unsummarized audio and archived audio
def manage_audio():
    all_raw = sorted_audio('data/raw_audio')
    notes_dir = os.path.join('data', 'notes')
    unarchived = [
        f for f in all_raw
        if not os.path.exists(
             os.path.join(notes_dir, os.path.splitext(f)[0] + '.json')
        )
    ]
    archived = sorted_audio('data/raw_audio_archive')
    return render_template('archive.html',
        unarchived=unarchived,
        archived=archived
    )
    
@main.route("/audio/transcribe_one", methods=["POST"]) #transcribes audio
def transcribe_one():
    data = request.get_json() or {}
    filename = data.get("file")
    if not filename:
        return jsonify(success=False, message="No file provided"), 400

    audio_path = os.path.join("data","raw_audio", filename)
    text = transcribe_file(audio_path) #function in transcribe.py communicating with open api whisper model
    if text is None:
        return jsonify(success=False, message=f"Error transcribing {filename}"), 500

    # save transcript
    base = os.path.splitext(filename)[0]
    transcript_path = os.path.join("data","transcripts", f"{base}.txt")
    with open(transcript_path, "w") as f:
        f.write(text)

    return jsonify(success=True, file=filename)

@main.route("/audio/summarize_one", methods=["POST"]) #summarize transcript
def summarize_one():
    data = request.get_json() or {}
    filename = data.get("file")
    if not filename:
        return jsonify(success=False, message="No file provided"), 400

    base = os.path.splitext(filename)[0]
    transcript_path = os.path.join("data","transcripts", f"{base}.txt")
    if not os.path.exists(transcript_path):
        return jsonify(success=False, message=f"No transcript for {filename}"), 404

    with open(transcript_path) as f:
        transcript = f.read()

    note = summarize_transcript(transcript) #structured output using 4o-mini
    if note is None:
        return jsonify(success=False, message=f"Error summarizing {filename}"), 500
    
    note["date"] = date_from_filename(base) #pull date from filename using helper function in utils
    note["transcript"] = transcript
    note_path = os.path.join("data","notes", f"{base}.json")
    with open(note_path, "w") as out:
        json.dump(note, out, indent=2)

    return jsonify(success=True, file=filename)

@main.route("/audio/archive", methods=["POST"]) #move audio to archive
def archive_audio():
    selected = request.form.getlist("files")
    for fn in selected:
        src = os.path.join("data","raw_audio",fn)
        dst = os.path.join("data","raw_audio_archive",fn)
        if os.path.exists(src):
            os.rename(src,dst)
    flash(f"Archived {len(selected)} file(s).")
    return redirect(request.referrer) #stay on page

@main.route("/audio/unarchive", methods=["POST"])
def unarchive_audio():
    selected = request.form.getlist("files")
    for fn in selected:
        src = os.path.join("data","raw_audio_archive",fn)
        dst = os.path.join("data","raw_audio",fn)
        if os.path.exists(src):
            os.rename(src,dst)
    flash(f"Unarchived {len(selected)} file(s).")
    return redirect(request.referrer)

@main.route("/api/recent-notes") #get the 5 most recent notes using util helper function
def recent_notes():
    notes = get_all_notes()[:5]
    return jsonify(notes)

@main.route("/api/available-audio") #keeps available audio list in sync without a full page reload
def available_audio():
    all_audio = sorted_audio('data/raw_audio')
    notes_dir = os.path.join('data','notes')

    available = [
        f for f in all_audio
        if not os.path.exists(os.path.join(notes_dir, os.path.splitext(f)[0] + '.json')
        )
    ]
    return jsonify(available)

@main.route('/transcripts')
def transcripts():
    all_transcripts = get_all_transcripts()
    return render_template('transcripts.html', transcripts=all_transcripts)