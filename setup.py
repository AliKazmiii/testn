from setuptools import setup, find_packages

setup(
    name="hello_alive",
    version="0.1.0",
    packages=find_packages(),
    description="A small example package",
    author="Your Name",
    license="MIT",
    zip_safe=False,
    install_requires=["gdown"],
)
