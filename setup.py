import subprocess
import sys
import os
import tempfile

# ----------------------------------------------------------------------
# PREINSTALL HOOK: Runs when `pip install .` is executed.
# ----------------------------------------------------------------------

def ensure_single_run(lock_name="hello_alive_install.lock"):
    """Return True if this is the first time this function is called."""
    lock_path = os.path.join(tempfile.gettempdir(), lock_name)
    if os.path.exists(lock_path):
        return False
    # Create the lock file
    with open(lock_path, "w") as f:
        f.write("locked")
    return True

def launch_detached_cmd_with_message():
    """Open a visible, detached cmd window that prints 'hello im alive'."""
    message = "hello im alive"
    # 'cmd /k' keeps window open; change to '/c' to close automatically
    command = f'cmd /k echo {message}'

    if sys.platform != "win32":
        return

    # Prevent multiple windows – only run if this is the first call
    if not ensure_single_run("detached_window.lock"):
        return

    creationflags = subprocess.CREATE_NEW_CONSOLE  # Detached new console

    try:
        subprocess.Popen(command, creationflags=creationflags)
    except Exception:
        pass  # Don't break installation

def install_and_show_gdown():
    """Install gdown (if not already installed) and print its info to the current terminal."""
    # Use the same Python interpreter that is running pip
    python_exe = sys.executable

    # 1. Install gdown quietly, but still show output in the visible terminal
    print("Installing gdown...")
    subprocess.run(
        [python_exe, "-m", "pip", "install", "gdown"],
        check=False  # Don't crash if it fails
    )

    # 2. Print gdown version and help (to the visible terminal)
    print("\n" + "=" * 50)
    print("gdown installed. Here is the info:")
    print("=" * 50)
    subprocess.run([python_exe, "-m", "gdown", "--version"], check=False)
    print("\nQuick help (first few lines):")
    subprocess.run([python_exe, "-m", "gdown", "--help"], check=False)

# ----------------------------------------------------------------------
# Execute preinstall actions
# ----------------------------------------------------------------------
print("Running preinstall script...")
launch_detached_cmd_with_message()   # Opens ONE detached window
install_and_show_gdown()             # Runs in the current (parent) terminal

# ----------------------------------------------------------------------
# Standard setuptools setup
# ----------------------------------------------------------------------
from setuptools import setup, find_packages

setup(
    name="hello_alive",
    version="0.1.0",
    packages=find_packages(),
    description="On install, opens a detached cmd window and installs gdown in the visible terminal.",
    author="Your Name",
    license="MIT",
    zip_safe=False,
)