import base64
import tempfile
import os
from flask import Flask, request
from translator import transcribe, translate_text, text_to_speech_bytes

app = Flask(__name__)

INDEX_HTML = """
<!doctype html>
<title>AITranslator</title>
<h1>Speech to Speech Translation</h1>
<form action="/translate" method="post" enctype="multipart/form-data">
  <p><input type="file" name="audio" accept="audio/*" required></p>
  <p>Target language code: <input name="target" value="de"></p>
  <p>Whisper model: <input name="whisper_model" value="base"></p>
  <p>EasyNMT model: <input name="easynmt_model" value="opus-mt"></p>
  <p>TTS lang code: <input name="tts_lang" value="a"></p>
  <p>Voice: <input name="voice" value="af_heart"></p>
  <p><button type="submit">Translate</button></p>
</form>
"""

@app.route("/")
def index():
    return INDEX_HTML

@app.route("/translate", methods=["POST"])
def translate_route():
    f = request.files.get("audio")
    if not f:
        return "Missing audio", 400
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        f.save(tmp.name)
        audio_path = tmp.name
    whisper_model = request.form.get("whisper_model", "base")
    easynmt_model = request.form.get("easynmt_model", "opus-mt")
    tts_lang = request.form.get("tts_lang", "a")
    voice = request.form.get("voice", "af_heart")
    target = request.form.get("target", "de")

    text = transcribe(audio_path, whisper_model)
    translated = translate_text(text, target, easynmt_model)
    audio_bytes = text_to_speech_bytes(translated, tts_lang, voice)
    os.remove(audio_path)

    b64 = base64.b64encode(audio_bytes).decode("utf-8")
    return (
        f"<h1>Result</h1><p>{translated}</p>"
        f"<audio controls src='data:audio/wav;base64,{b64}'></audio>"
        "<p><a href='/'>Back</a></p>"
    )

if __name__ == "__main__":
    app.run(debug=True)
