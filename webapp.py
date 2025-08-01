import base64
import tempfile
import os
import subprocess
from flask import Flask, request
from translator import transcribe, translate_text, text_to_speech_bytes

REST_URL = os.getenv("EASYNMT_REST_URL", "http://easynmt-api/translate")
USE_LOCAL = os.getenv("USE_LOCAL_EASYNMT", "false").lower() in ("1", "true", "yes")

app = Flask(__name__)


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

INDEX_HTML = """
<!doctype html>
<title>AITranslator</title>
<h1>Speech to Speech Translation</h1>
<form id="uploadForm" action="/translate" method="post" enctype="multipart/form-data">
  <p><input id="audioInput" type="file" name="audio" accept="audio/*" required></p>
  <p>Target language code: <input name="target" value="de"></p>
  <p>Whisper model: <input name="whisper_model" value="base"></p>
  <p>EasyNMT model: <input name="easynmt_model" value="opus-mt"></p>
  <p>TTS lang code: <input name="tts_lang" value="a"></p>
  <p>Voice: <input name="voice" value="af_heart"></p>
  <p><button type="submit">Translate</button></p>
</form>

<h2>Microphone</h2>
<p>
  <button type="button" id="startRecord">Start Recording</button>
  <button type="button" id="stopRecord" disabled>Stop</button>
</p>
<p><audio id="recordedAudio" controls style="display:none"></audio></p>

<script>
let mediaRecorder;
let chunks = [];
const startBtn = document.getElementById('startRecord');
const stopBtn = document.getElementById('stopRecord');
const audioElem = document.getElementById('recordedAudio');
const fileInput = document.getElementById('audioInput');

startBtn.onclick = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({audio: true});
    chunks = [];
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = e => chunks.push(e.data);
    mediaRecorder.onstop = () => {
      const blob = new Blob(chunks, {type: 'audio/webm'});
      const file = new File([blob], 'recording.webm', {type: 'audio/webm'});
      const dt = new DataTransfer();
      dt.items.add(file);
      fileInput.files = dt.files;
      audioElem.src = URL.createObjectURL(blob);
      audioElem.style.display = 'block';
    };
    mediaRecorder.start();
    startBtn.disabled = true;
    stopBtn.disabled = false;
  } catch(err) {
    alert('Could not start recording: ' + err);
  }
};

stopBtn.onclick = () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
  }
  startBtn.disabled = false;
  stopBtn.disabled = true;
};
</script>
"""

@app.route("/")
def index():
    return INDEX_HTML

@app.route("/translate", methods=["POST"])
def translate_route():
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
        f"<audio controls src='data:audio/wav;base64,{b64}'></audio>"
        "<p><a href='/'>Back</a></p>"
    )

if __name__ == "__main__":
    app.run(debug=True)
