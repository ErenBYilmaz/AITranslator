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
