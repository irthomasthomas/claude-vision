from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="claude-vision",
    version="0.2.0",
    author="Your Name",
    author_email="irthomasthomas@gmail.com",
    description="An advanced CLI tool for image analysis using Claude 3.5 Sonnet",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/irthomasthomas/claude-vision",
    packages=find_packages(),
    install_requires=[
        "click",
        "pillow",
        "requests",
        "pyyaml",  # For configuration files
    ],
    entry_points={
        "console_scripts": [
            "claude-vision=claude_vision.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
)