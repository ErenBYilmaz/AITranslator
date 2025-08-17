import argparse
import logging

import whisper
from kokoro import KPipeline
import soundfile as sf
import sounddevice as sd
import tempfile
from typing import Optional
import io
import numpy as np
import requests


def record_from_microphone(duration: int = 5, sample_rate: int = 16000) -> str:
    """Record audio from the microphone and write it to a temporary wav file."""
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    sf.write(temp.name, recording, sample_rate)
    return temp.name


def transcribe(audio_file: str, model_name: str = "base") -> str:
    logging.info('Transcribing audio file: %s with model: %s', audio_file, model_name)
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_file)
    return result.get("text", "")


def translate_text(
    text: str,
    target_lang: str,
    model_name: str = "opus-mt",
    rest_url: Optional[str] = None,
) -> str:
    """Translate text either locally with EasyNMT or via the REST API."""
    logging.info('Translating text: "%s" to language: %s using model: %s', text, target_lang, model_name)
    if rest_url:
        resp = requests.get(rest_url, params={ "target_lang": target_lang, "text": text,})
        resp.raise_for_status()
        data = resp.json()
        translated = data.get("translated")
        if isinstance(translated, list):
            return " ".join(translated)
        return str(translated)
    from easynmt import EasyNMT
    translator = EasyNMT(model_name)
    return translator.translate(text, target_lang=target_lang)


def text_to_speech(
    text: str,
    lang_code: str = "a",
    voice: str = "af_heart",
    play: bool = False,
) -> None:
    """Generate speech from text and either save or play it."""
    pipeline = KPipeline(lang_code=lang_code)
    generator = pipeline(text, voice=voice)
    for i, (_, _, audio) in enumerate(generator):
        if play:
            sd.play(audio, 24000)
            sd.wait()
        else:
            sf.write(f"output_{i}.wav", audio, 24000)


def text_to_speech_bytes(
    text: str,
    lang_code: str = "a",
    voice: str = "af_heart",
) -> bytes:
    """Return generated speech as WAV bytes."""
    pipeline = KPipeline(lang_code=lang_code)
    generator = pipeline(text, voice=voice)
    audio_segments = []
    for _, _, audio in generator:
        audio_segments.append(audio)
    if not audio_segments:
        return b""
    combined = np.concatenate(audio_segments)
    buffer = io.BytesIO()
    sf.write(buffer, combined, 24000, format="wav")
    buffer.seek(0)
    return buffer.read()


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcribe, translate and speak audio")
    parser.add_argument("target_lang", help="Target language code for translation")
    parser.add_argument("audio", nargs="?", help="Path to an audio file")
    parser.add_argument("--whisper-model", default="base", dest="whisper_model", help="Whisper model to use")
    parser.add_argument("--easynmt-model", default="opus-mt", dest="easynmt_model", help="EasyNMT model to use")
    parser.add_argument(
        "--rest-url",
        default="http://easynmt-api/translate",
        help="EasyNMT REST API endpoint. Use empty string to run locally.",
    )
    parser.add_argument(
        "--use-local-easynmt",
        action="store_true",
        help="Use local EasyNMT instead of REST API",
    )
    parser.add_argument("--tts-lang", default="a", dest="tts_lang", help="Kokoro language code")
    parser.add_argument("--voice", default="af_heart", help="Voice name for Kokoro")
    parser.add_argument("--mic", action="store_true", help="Record from microphone instead of file")
    parser.add_argument("--duration", type=int, default=5, help="Recording duration when using microphone")
    parser.add_argument("--play", action="store_true", help="Play audio instead of saving to disk")
    args = parser.parse_args()

    if args.mic:
        audio_path = record_from_microphone(args.duration)
    else:
        if not args.audio:
            parser.error("Audio file path is required unless --mic is used")
        audio_path = args.audio

    rest_url = None if args.use_local_easynmt or not args.rest_url else args.rest_url

    text = transcribe(audio_path, args.whisper_model)
    translated = translate_text(
        text,
        args.target_lang,
        args.easynmt_model,
        rest_url=rest_url,
    )
    print(translated)
    text_to_speech(translated, args.tts_lang, args.voice, play=args.play)


if __name__ == "__main__":
    main()
