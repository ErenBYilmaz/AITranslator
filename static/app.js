let mediaRecorder;
let chunks = [];
const recordBtn = document.getElementById('recordButton');
const audioElem = document.getElementById('recordedAudio');
const fileInput = document.getElementById('audioInput');
const formElem = document.getElementById('uploadForm');
const targetSelect = document.querySelector('select[name="target"]');
const recentContainerParent = document.getElementById('recent-languages-container');
const recentContainer = document.getElementById('recent-languages');
const RECENT_KEY = 'recentLanguages';
const MAX_RECENT = 5;

function renderRecent() {
  const recent = JSON.parse(localStorage.getItem(RECENT_KEY) || '[]');
  if (recent.length === 0) {
    recentContainerParent.style.display = 'none';
    return;
  }
  recentContainerParent.style.display = 'block';
  recentContainer.innerHTML = '';
  recent.forEach(code => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = code;
    btn.addEventListener('click', () => {
      targetSelect.value = code;
    });
    recentContainer.appendChild(btn);
  });
}

renderRecent();

formElem.addEventListener('submit', () => {
  const selected = targetSelect.value;
  let recent = JSON.parse(localStorage.getItem(RECENT_KEY) || '[]');
  recent = recent.filter(c => c !== selected);
  recent.unshift(selected);
  if (recent.length > MAX_RECENT) {
    recent = recent.slice(0, MAX_RECENT);
  }
  localStorage.setItem(RECENT_KEY, JSON.stringify(recent));
});

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
