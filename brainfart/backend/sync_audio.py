import os
import sys
import shutil

def sync_audio():
    device_mount = "/media/pi/USB-DISK"          #path to audio files
    #device_mount = "D:/"
    audio_dir    = os.path.join(device_mount, "RECORD") 
    dest_dir     = os.path.join("data", "raw_audio") 
    archive_dir = os.path.join("data", "raw_audio_archive")

    if not os.path.isdir(audio_dir): #make sure the device is connected
        return {"status": "no_device"}

    os.makedirs(dest_dir, exist_ok=True) #make sure destination file exists

    new_files = [] #copy new files (not in archive or already summarized)
    for f in os.listdir(audio_dir):
        if f.lower().endswith((".mp3", ".wav", ".m4a", ".WAV")):
            src = os.path.join(audio_dir, f)
            dst = os.path.join(dest_dir, f)
            archive_path = os.path.join(archive_dir, f)
            if not os.path.exists(dst) and not os.path.exists(archive_path):
                shutil.copy(src, dst)
                new_files.append(f)

    if not new_files:
        return {"status": "no_new_audio"}
    else:
        return {"status": "new_audio", "files": new_files}

if __name__ == "__main__":
    result = sync_audio()
    if result["status"] == "no_device":
        print("NO_DEVICE")
        sys.exit(0)
    if result["status"] == "no_new_audio":
        print("NO_NEW_AUDIO")
        sys.exit(0)
    print("NEW_AUDIO:" + ",".join(result["files"]))
    sys.exit(0)
