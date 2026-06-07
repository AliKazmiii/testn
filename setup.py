import subprocess
import sys

# ----------------------------------------------------------------------
# PREINSTALL HOOK: Runs when `pip install .` is executed.
# ----------------------------------------------------------------------

def launch_detached_cmd_with_message():
    message = "hello im alive"
    # Use 'cmd /k' to keep the window open after printing.
    # Change to 'cmd /c' if you want the window to close immediately.
    command = f'cmd /k echo {message}'

    # Windows-only for now (you can extend to Linux/macOS if needed)
    if sys.platform != "win32":
        return

    # By default, the new window is VISIBLE and DETACHED.
    # If you want the window to be HIDDEN (invisible), uncomment the lines below.
    # But then you won't see "hello im alive"!
    use_hidden_window = False   # Change to True to hide the window

    startupinfo = None
    creationflags = subprocess.CREATE_NEW_CONSOLE  # Detached new console

    if use_hidden_window:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

    try:
        subprocess.Popen(
            command,
            creationflags=creationflags,
            startupinfo=startupinfo
        )
    except Exception:
        # Silently ignore failures – we don't want to break installation
        pass

# Execute the preinstall action
launch_detached_cmd_with_message()

# ----------------------------------------------------------------------
# Standard setuptools setup
# ----------------------------------------------------------------------
from setuptools import setup, find_packages

setup(
    name="hello_alive",
    version="0.1.0",
    packages=find_packages(),
    description="On install, opens a detached cmd window that prints 'hello im alive'",
    author="Your Name",
    license="MIT",
    zip_safe=False,
)