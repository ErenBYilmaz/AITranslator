# AITranslator

This project provides a minimal pipeline for speech translation. It uses OpenAI's Whisper to transcribe audio, EasyNMT for language translation, and Kokoro for text‑to‑speech synthesis. By default the generated audio is written to disk as `output_N.wav`.

## Requirements
Install the dependencies from `requirements.txt`:
```bash
pip install -r requirements.txt
```

On some systems you may also need [`ffmpeg`](https://ffmpeg.org/) and `espeak-ng` for audio processing.

## Usage
```
python translator.py de input.wav
```
This will transcribe `input.wav`, translate the text to German and generate speech audio files using Kokoro.

### Microphone mode
You can also record from the microphone and play the translated speech directly through the speakers:

```
python translator.py de --mic --play
```

Use `--duration` to specify the recording time in seconds.

## Web interface
You can launch a small web application with:

```bash
python webapp.py
```

Open <http://localhost:5000> in your browser to upload an audio file. The page
will show the translated text and an audio player with the generated speech.

## Docker
You can also run the translator inside a container. Build the image and run the CLI:
```bash
docker build -t aitranslator .
docker run --rm -it aitranslator --help
```

With Docker Compose:
```bash
docker compose run translator --help
```

To test the web interface with Docker Compose:
```bash
docker compose up web
```
