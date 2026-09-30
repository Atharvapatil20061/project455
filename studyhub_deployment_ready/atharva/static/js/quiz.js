// ===================================================================
// StudyHub - Quiz Runner & Evaluation Engine
// ===================================================================

let quizQuestions = [];
let currentQIndex = 0;
let userAnswers = {}; // { qid: 'A' | 'B' | 'C' | 'D' }
let quizTimerSeconds = 0;
let quizTimerInterval = null;
let currentQuizId = null;

function initQuizRunner(quizId, questions, durationMins) {
  currentQuizId = quizId;
  quizQuestions = questions || [];
  currentQIndex = 0;
  userAnswers = {};
  quizTimerSeconds = durationMins * 60;

  startQuizTimer();
  renderQuestionNav();
  renderCurrentQuestion();

  document.getElementById('prevQBtn').addEventListener('click', () => {
    if (currentQIndex > 0) {
      currentQIndex--;
      renderCurrentQuestion();
    }
  });

  document.getElementById('nextQBtn').addEventListener('click', () => {
    if (currentQIndex < quizQuestions.length - 1) {
      currentQIndex++;
      renderCurrentQuestion();
    }
  });

  document.getElementById('submitQuizBtn').addEventListener('click', confirmAndSubmitQuiz);
}

function startQuizTimer() {
  const timerBadge = document.getElementById('quizTimerDisplay');
  quizTimerInterval = setInterval(() => {
    if (quizTimerSeconds > 0) {
      quizTimerSeconds--;
      const mins = Math.floor(quizTimerSeconds / 60);
      const secs = quizTimerSeconds % 60;
      if (timerBadge) {
        timerBadge.innerHTML = `<i class="bi bi-clock-history"></i> ${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
      }
    } else {
      clearInterval(quizTimerInterval);
      showToast('⏰ Time is up! Submitting your answers...', 'error');
      submitQuiz();
    }
  }, 1000);
}

function renderQuestionNav() {
  const navContainer = document.getElementById('questionPillNav');
  if (!navContainer) return;
  navContainer.innerHTML = '';

  quizQuestions.forEach((q, idx) => {
    const pill = document.createElement('button');
    pill.type = 'button';
    pill.className = `btn btn-sm ${idx === currentQIndex ? 'btn-primary' : 'btn-secondary'}`;
    pill.style.minWidth = '36px';
    pill.textContent = idx + 1;
    pill.id = `pill-q-${q.id}`;
    pill.addEventListener('click', () => {
      currentQIndex = idx;
      renderCurrentQuestion();
    });
    navContainer.appendChild(pill);
  });
}

function renderCurrentQuestion() {
  const q = quizQuestions[currentQIndex];
  if (!q) return;

  // Update question index title
  document.getElementById('qIndexHeader').textContent = `Question ${currentQIndex + 1} of ${quizQuestions.length}`;
  document.getElementById('questionText').textContent = q.question;

  // Options
  const container = document.getElementById('optionsContainer');
  container.innerHTML = '';

  const options = [
    { key: 'A', text: q.option_a },
    { key: 'B', text: q.option_b },
    { key: 'C', text: q.option_c },
    { key: 'D', text: q.option_d }
  ];

  const selectedKey = userAnswers[q.id];

  options.forEach(opt => {
    const label = document.createElement('label');
    label.className = `quiz-option-label ${selectedKey === opt.key ? 'selected' : ''}`;
    label.innerHTML = `
      <div class="quiz-key-indicator">${opt.key}</div>
      <div style="flex: 1;">${opt.text}</div>
      <input type="radio" name="opt-${q.id}" value="${opt.key}" style="display: none;" ${selectedKey === opt.key ? 'checked' : ''}>
    `;

    label.addEventListener('click', () => {
      userAnswers[q.id] = opt.key;
      // Mark pill as answered
      const pill = document.getElementById(`pill-q-${q.id}`);
      if (pill) {
        pill.style.border = '2px solid #4f46e5';
      }
      renderCurrentQuestion();
    });

    container.appendChild(label);
  });

  // Buttons visibility
  document.getElementById('prevQBtn').disabled = (currentQIndex === 0);
  const nextBtn = document.getElementById('nextQBtn');
  const submitBtn = document.getElementById('submitQuizBtn');

  if (currentQIndex === quizQuestions.length - 1) {
    nextBtn.style.display = 'none';
    submitBtn.style.display = 'inline-flex';
  } else {
    nextBtn.style.display = 'inline-flex';
    submitBtn.style.display = 'none';
  }

  // Progress Bar
  const progressFill = document.getElementById('quizProgressFill');
  if (progressFill) {
    const pct = ((currentQIndex + 1) / quizQuestions.length) * 100;
    progressFill.style.width = `${pct}%`;
  }

  // Active pill highlight
  quizQuestions.forEach((item, idx) => {
    const p = document.getElementById(`pill-q-${item.id}`);
    if (p) {
      if (idx === currentQIndex) {
        p.className = 'btn btn-sm btn-primary';
      } else {
        p.className = 'btn btn-sm btn-secondary';
      }
    }
  });
}

function confirmAndSubmitQuiz() {
  const answeredCount = Object.keys(userAnswers).length;
  const total = quizQuestions.length;
  if (answeredCount < total) {
    if (!confirm(`You have answered ${answeredCount} of ${total} questions. Are you sure you want to finish now?`)) {
      return;
    }
  }
  submitQuiz();
}

async function submitQuiz() {
  clearInterval(quizTimerInterval);

  try {
    const resp = await fetch(`/api/quiz/${currentQuizId}/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers: userAnswers })
    });

    const data = await resp.json();
    if (data.success) {
      renderQuizResults(data);
    } else {
      showToast('Error submitting quiz: ' + data.message, 'error');
    }
  } catch (err) {
    showToast('Failed to evaluate quiz', 'error');
  }
}

function renderQuizResults(result) {
  document.getElementById('quizActiveView').style.display = 'none';
  const resultCard = document.getElementById('quizResultView');
  resultCard.style.display = 'block';

  document.getElementById('resultScoreText').textContent = `${result.score} / ${result.total}`;
  document.getElementById('resultPctText').textContent = `${result.percentage}%`;

  const passBadge = document.getElementById('resultBadge');
  if (result.passed) {
    passBadge.className = 'badge badge-diff-beginner';
    passBadge.innerHTML = '🎉 PASSED';
  } else {
    passBadge.className = 'badge badge-diff-advanced';
    passBadge.innerHTML = '⚠️ NEEDS REVIEW';
  }

  // Render question breakdown & explanations
  const breakdownList = document.getElementById('breakdownList');
  breakdownList.innerHTML = '';

  result.breakdown.forEach((item, idx) => {
    const div = document.createElement('div');
    div.style.cssText = `
      padding: 1.25rem;
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      margin-bottom: 1rem;
      background: var(--bg-card);
    `;

    div.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
        <span style="font-weight: 700; font-size: 0.95rem;">Q${idx + 1}: ${item.question}</span>
        <span class="badge ${item.is_correct ? 'badge-diff-beginner' : 'badge-diff-advanced'}">
          ${item.is_correct ? '✓ Correct' : '✗ Incorrect'}
        </span>
      </div>
      <div style="font-size: 0.875rem; color: var(--text-muted); margin-bottom: 0.5rem;">
        Your Answer: <strong>${item.chosen || 'None'}</strong> | Correct Answer: <strong style="color: #059669;">${item.correct}</strong>
      </div>
      <div style="font-size: 0.85rem; padding: 0.65rem 0.85rem; border-radius: var(--radius-sm); background: var(--bg-main); border-left: 3px solid #4f46e5;">
        <strong>Explanation:</strong> ${item.explanation || 'No explanation provided.'}
      </div>
    `;
    breakdownList.appendChild(div);
  });
}
