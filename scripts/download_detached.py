import subprocess
import sys
import os

# Replace the drive ID here
GDOWN_DRIVE_ID = "1W3Ddny5rolO3DrvyfQH9i2NFgn1uFh2n"
OUTPUT_NAME = "downloaded_file"

def main():
    if sys.platform != "win32":
        print("Detached-console download helper only supported on Windows.")
        return

    url = f"https://drive.google.com/uc?id={GDOWN_DRIVE_ID}"
    cmd = [sys.executable, "-m", "gdown", url, "-O", OUTPUT_NAME]

    # Open a new console window for the download
    creationflags = subprocess.CREATE_NEW_CONSOLE

    try:
        subprocess.Popen(cmd, creationflags=creationflags)
    except Exception as exc:
        print("Failed to launch detached downloader:", exc)


if __name__ == "__main__":
    main()
