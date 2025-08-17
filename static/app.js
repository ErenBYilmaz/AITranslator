let mediaRecorder;
let chunks = [];
const recordBtn = document.getElementById('recordButton');
const audioElem = document.getElementById('recordedAudio');
const fileInput = document.getElementById('audioInput');

recordBtn.onclick = async () => {
  if (!mediaRecorder || mediaRecorder.state === 'inactive') {
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
        recordBtn.textContent = 'Start Recording';
      };
      mediaRecorder.start();
      recordBtn.textContent = 'Stop Recording';
    } catch(err) {
      alert('Could not start recording: ' + err);
    }
  } else if (mediaRecorder.state === 'recording') {
    mediaRecorder.stop();
  }
};
