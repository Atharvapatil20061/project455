// ===================================================================
// StudyHub - Pomodoro Timer & Audio Synthesizer Engine
// ===================================================================

let timerInterval = null;
let totalTime = 25 * 60;
let timeRemaining = 25 * 60;
let isRunning = false;
let currentMode = 'pomodoro'; // 'pomodoro', 'shortBreak', 'longBreak'
let completedSessionsCount = 0;

// Web Audio API Context
let audioCtx = null;
let ambientSource = null;
let ambientGain = null;
let currentAmbientType = 'none';

document.addEventListener('DOMContentLoaded', () => {
  initPomodoro();
  initAmbientControls();
});

function initPomodoro() {
  const playBtn = document.getElementById('playPauseBtn');
  const resetBtn = document.getElementById('resetBtn');
  const skipBtn = document.getElementById('skipBtn');
  const modePills = document.querySelectorAll('.timer-pill');

  updateTimerDisplay();

  if (playBtn) {
    playBtn.addEventListener('click', togglePlayPause);
  }
  if (resetBtn) {
    resetBtn.addEventListener('click', resetTimer);
  }
  if (skipBtn) {
    skipBtn.addEventListener('click', skipTimer);
  }

  modePills.forEach(pill => {
    pill.addEventListener('click', () => {
      modePills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      setMode(pill.getAttribute('data-mode'));
    });
  });
}

function setMode(mode) {
  clearInterval(timerInterval);
  isRunning = false;
  currentMode = mode;

  const playBtn = document.getElementById('playPauseBtn');
  if (playBtn) playBtn.innerHTML = '<i class="bi bi-play-fill"></i>';

  const statusLabel = document.getElementById('timerStatusLabel');

  if (mode === 'pomodoro') {
    totalTime = 25 * 60;
    if (statusLabel) statusLabel.textContent = 'Focus Session';
    setCircleColor('#4f46e5');
  } else if (mode === 'shortBreak') {
    totalTime = 5 * 60;
    if (statusLabel) statusLabel.textContent = 'Short Break';
    setCircleColor('#10b981');
  } else if (mode === 'longBreak') {
    totalTime = 15 * 60;
    if (statusLabel) statusLabel.textContent = 'Long Break';
    setCircleColor('#06b6d4');
  }

  timeRemaining = totalTime;
  updateTimerDisplay();
}

function togglePlayPause() {
  const playBtn = document.getElementById('playPauseBtn');
  if (isRunning) {
    clearInterval(timerInterval);
    isRunning = false;
    if (playBtn) playBtn.innerHTML = '<i class="bi bi-play-fill"></i>';
  } else {
    isRunning = true;
    if (playBtn) playBtn.innerHTML = '<i class="bi bi-pause-fill"></i>';
    timerInterval = setInterval(() => {
      if (timeRemaining > 0) {
        timeRemaining--;
        updateTimerDisplay();
      } else {
        onTimerComplete();
      }
    }, 1000);
  }
}

function resetTimer() {
  clearInterval(timerInterval);
  isRunning = false;
  timeRemaining = totalTime;
  const playBtn = document.getElementById('playPauseBtn');
  if (playBtn) playBtn.innerHTML = '<i class="bi bi-play-fill"></i>';
  updateTimerDisplay();
}

function skipTimer() {
  if (confirm('Skip to the next study session / break?')) {
    if (currentMode === 'pomodoro') {
      completedSessionsCount++;
      const nextMode = (completedSessionsCount % 4 === 0) ? 'longBreak' : 'shortBreak';
      selectModePill(nextMode);
    } else {
      selectModePill('pomodoro');
    }
  }
}

function selectModePill(mode) {
  const pill = document.querySelector(`.timer-pill[data-mode="${mode}"]`);
  if (pill) pill.click();
}

function updateTimerDisplay() {
  const minutes = Math.floor(timeRemaining / 60);
  const seconds = timeRemaining % 60;
  const formatted = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

  const timeEl = document.getElementById('timerDisplay');
  if (timeEl) timeEl.textContent = formatted;

  document.title = `${formatted} - ${currentMode === 'pomodoro' ? 'Focusing' : 'Break'} | StudyHub`;

  // Update SVG Circle Progress
  const circle = document.getElementById('timerProgressCircle');
  if (circle) {
    const circumference = 2 * Math.PI * 135; // radius = 135
    circle.style.strokeDasharray = circumference;
    const progress = (totalTime - timeRemaining) / totalTime;
    const offset = circumference - (progress * circumference);
    circle.style.strokeDashoffset = offset;
  }
}

function setCircleColor(color) {
  const circle = document.getElementById('timerProgressCircle');
  if (circle) circle.style.stroke = color;
}

function onTimerComplete() {
  clearInterval(timerInterval);
  isRunning = false;
  playChime();

  if (currentMode === 'pomodoro') {
    completedSessionsCount++;
    const countDisplay = document.getElementById('completedCount');
    if (countDisplay) countDisplay.textContent = completedSessionsCount;

    // Log to backend
    fetch('/api/pomodoro/log', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ duration_mins: Math.round(totalTime / 60), subject: 'Pomodoro Focus' })
    }).catch(err => console.error(err));

    showToast('🎉 Fantastic job! 25 minutes of deep focus complete!', 'success');

    // Auto transition to break
    const nextMode = (completedSessionsCount % 4 === 0) ? 'longBreak' : 'shortBreak';
    setTimeout(() => selectModePill(nextMode), 1500);
  } else {
    showToast('⚡ Break is finished! Time to dive back in.', 'info');
    setTimeout(() => selectModePill('pomodoro'), 1500);
  }
}

// ----------------- Web Audio API Synthesizers -----------------

function getAudioContext() {
  if (!audioCtx) {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    audioCtx = new AudioContextClass();
  }
  if (audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
  return audioCtx;
}

// Chime on Timer End
function playChime() {
  try {
    const ctx = getAudioContext();
    const now = ctx.currentTime;

    // Create 3 harmonic chime tones
    [523.25, 659.25, 783.99].forEach((freq, idx) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, now + idx * 0.12);

      gain.gain.setValueAtTime(0, now);
      gain.gain.linearRampToValueAtTime(0.2, now + idx * 0.12 + 0.05);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + idx * 0.12 + 1.8);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(now + idx * 0.12);
      osc.stop(now + idx * 0.12 + 2.0);
    });
  } catch (err) {
    console.warn('Audio synthesis not supported or blocked:', err);
  }
}

// Ambient Sound Synthesizer (White Noise, Rain, Lo-Fi, Brown Noise)
function initAmbientControls() {
  const chips = document.querySelectorAll('.sound-chip');
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      const type = chip.getAttribute('data-sound');
      if (currentAmbientType === type) {
        stopAmbientSound();
        chips.forEach(c => c.classList.remove('active'));
        currentAmbientType = 'none';
      } else {
        chips.forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        playAmbientSound(type);
      }
    });
  });
}

function stopAmbientSound() {
  if (ambientSource) {
    try {
      ambientSource.stop();
      ambientSource.disconnect();
    } catch(e) {}
    ambientSource = null;
  }
  const eq = document.getElementById('ambientEqualizer');
  if (eq) eq.classList.remove('playing');
}

function playAmbientSound(type) {
  stopAmbientSound();
  currentAmbientType = type;
  if (type === 'none') return;

  const eq = document.getElementById('ambientEqualizer');
  if (eq) eq.classList.add('playing');

  try {
    const ctx = getAudioContext();
    const bufferSize = ctx.sampleRate * 2;
    const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const output = noiseBuffer.getChannelData(0);

    let lastOut = 0.0;
    for (let i = 0; i < bufferSize; i++) {
      const white = Math.random() * 2 - 1;
      if (type === 'rain') {
        // Pink / filtered noise for rain simulation
        output[i] = (lastOut + (0.02 * white)) / 1.02;
        lastOut = output[i];
      } else if (type === 'whitenoise') {
        output[i] = white * 0.3;
      } else if (type === 'brown') {
        output[i] = (lastOut + (0.05 * white)) / 1.05;
        lastOut = output[i];
      } else {
        output[i] = (lastOut + (0.03 * white)) / 1.03;
        lastOut = output[i];
      }
    }

    ambientSource = ctx.createBufferSource();
    ambientSource.buffer = noiseBuffer;
    ambientSource.loop = true;

    // Filter for pleasant smooth frequency
    const filter = ctx.createBiquadFilter();
    if (type === 'rain') {
      filter.type = 'lowpass';
      filter.frequency.value = 850;
    } else if (type === 'lofi') {
      filter.type = 'bandpass';
      filter.frequency.value = 500;
      filter.Q.value = 1.5;
    } else {
      filter.type = 'lowpass';
      filter.frequency.value = 1200;
    }

    ambientGain = ctx.createGain();
    ambientGain.gain.setValueAtTime(0.08, ctx.currentTime);

    ambientSource.connect(filter);
    filter.connect(ambientGain);
    ambientGain.connect(ctx.destination);

    ambientSource.start();
  } catch (err) {
    console.warn('Could not synthesize ambient audio:', err);
  }
}
