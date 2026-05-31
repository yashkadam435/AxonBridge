#!/usr/bin/env python3
"""
Downloads lightweight model weights on build for the demo.
"""

import os
from faster_whisper import WhisperModel

MODELS_DIR = "/app/models"
os.makedirs(MODELS_DIR, exist_ok=True)

def download():
    print("Downloading lightweight Whisper tiny.en model (~150MB)...")
    WhisperModel("tiny.en", download_root=f"{MODELS_DIR}/whisper", compute_type="int8")
    
    print("All models downloaded successfully for the lightweight demo!")

if __name__ == "__main__":
    download()
