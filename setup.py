
from setuptools import setup, find_packages

setup(
    name="claude-vision",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "click",
        "httpx",
        "Pillow",
        "pyyaml",
        "jsonschema",
    ],
    entry_points={
        "console_scripts": [
            "claude-vision=claude_vision.cli:cli",
        ],
    },
    author="Thomas Hughes",
    author_email="irthomasthomas@gmail.com",
    description="A CLI tool for advanced image analysis using Claude API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/irthomasthomas/claude-vision",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)