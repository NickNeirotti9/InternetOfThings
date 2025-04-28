Brainfart is a lightweight, Python-based web application that allows users to sync, transcribe, summarize, and manage voice notes.

To run this code:
1) git clone https://github.com/NickNeirotti9/InternetOfThings.git
2) cd InternetOfThings/brainfart
3) pip install -r requirements.txt
4) Create a file called .env inside the brainfart/ directory and add "OPENAI_API_KEY="
5) New-Item -ItemType Directory -Force -Path data\raw_audio, data\raw_audio_archive, data\transcripts, data\notes
6) Modify backend/sync_audio.py device_mount with the path of your device
7) python run.py

