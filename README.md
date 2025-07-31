# AITranslator

This project provides a minimal pipeline for speech translation. It uses OpenAI's Whisper to transcribe audio, EasyNMT for language translation, and Kokoro for text‑to‑speech synthesis. The resulting audio files are written to disk as `output_N.wav`.

## Requirements
Install the dependencies from `requirements.txt`:
```bash
pip install -r requirements.txt
```

On some systems you may also need [`ffmpeg`](https://ffmpeg.org/) and `espeak-ng` for audio processing.

## Usage
```
python translator.py input.wav de
```
This will transcribe `input.wav`, translate the text to German and generate speech audio files using Kokoro.
