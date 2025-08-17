import base64
import logging
import tempfile
import os
import subprocess
from flask import Flask, request, render_template
from translator import transcribe, translate_text, text_to_speech_bytes
from typing import List

REST_URL = os.getenv("EASYNMT_REST_URL", "http://localhost:24080/translate")
USE_LOCAL = os.getenv("USE_LOCAL_EASYNMT", "false").lower() in ("1", "true", "yes")

app = Flask(__name__)


def _load_supported_languages() -> List[str]:
    """Parse the notes/easynmt.md file and extract supported language codes."""
    langs = set()
    notes_path = os.path.join(os.path.dirname(__file__), "notes", "easynmt.md")
    try:
        with open(notes_path, "r", encoding="utf-8") as fh:
            for line in fh:
                if "**Supported languages" in line:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        for code in parts[1].split(","):
                            code = code.strip().strip("*").strip()
                            if code:
                                langs.add(code)
    except FileNotFoundError:
        pass
    return sorted(langs)


SUPPORTED_LANGUAGES = _load_supported_languages()


def convert_to_wav(input_path: str) -> str:
    """Convert an audio file to WAV format using ffmpeg."""
    if input_path.lower().endswith(".wav"):
        return input_path
    out_fd = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    out_path = out_fd.name
    out_fd.close()
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        "-ac",
        "1",
        "-ar",
        "16000",
        out_path,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(input_path)
    return out_path


@app.route("/")
def index():
    return render_template("index.html", languages=SUPPORTED_LANGUAGES)


@app.route("/translate", methods=["POST"])
def translate_route():
    logging.info('Translation request received')
    f = request.files.get("audio")
    if not f:
        return "Missing audio", 400
    ext = os.path.splitext(f.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext or ".dat") as tmp:
        f.save(tmp.name)
        audio_path = tmp.name
    audio_path = convert_to_wav(audio_path)
    whisper_model = request.form.get("whisper_model", "base")
    easynmt_model = request.form.get("easynmt_model", "opus-mt")
    tts_lang = request.form.get("tts_lang", "a")
    voice = request.form.get("voice", "af_heart")
    target = request.form.get("target", "de")

    rest_url = None if USE_LOCAL else REST_URL
    text = transcribe(audio_path, whisper_model)
    translated = translate_text(text, target, easynmt_model, rest_url=rest_url)
    audio_bytes = text_to_speech_bytes(translated, tts_lang, voice)
    os.remove(audio_path)

    b64 = base64.b64encode(audio_bytes).decode("utf-8")
    return (
        f"<h1>Result</h1><p>{translated}</p>"
        f"<audio controls autoplay src='data:audio/wav;base64,{b64}'></audio>"
        "<p><a href='/'>Back</a></p>"
    )


if __name__ == "__main__":
    app.run(debug=True)
