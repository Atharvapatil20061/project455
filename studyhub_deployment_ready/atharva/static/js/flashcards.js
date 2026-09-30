// ===================================================================
// StudyHub - Flashcards Spaced Repetition Engine
// ===================================================================

let flashcardsData = [];
let currentIndex = 0;
let cardStats = { easy: 0, med: 0, hard: 0 };

function initFlashcards(cards) {
  flashcardsData = cards || [];
  currentIndex = 0;
  cardStats = { easy: 0, med: 0, hard: 0 };

  const cardBox = document.getElementById('flashcardBox');
  const prevBtn = document.getElementById('prevCardBtn');
  const nextBtn = document.getElementById('nextCardBtn');
  const shuffleBtn = document.getElementById('shuffleCardsBtn');
  const flipBtn = document.getElementById('flipCardBtn');

  if (cardBox) {
    cardBox.addEventListener('click', toggleCardFlip);
  }
  if (flipBtn) {
    flipBtn.addEventListener('click', toggleCardFlip);
  }
  if (prevBtn) {
    prevBtn.addEventListener('click', prevCard);
  }
  if (nextBtn) {
    nextBtn.addEventListener('click', nextCard);
  }
  if (shuffleBtn) {
    shuffleBtn.addEventListener('click', shuffleCards);
  }

  // Rate Buttons
  document.querySelectorAll('.btn-rate').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const rating = btn.getAttribute('data-rating');
      rateCard(rating);
    });
  });

  // Keyboard Navigation: Space = flip, Left = Prev, Right = Next, 1=Hard, 2=Med, 3=Easy
  document.addEventListener('keydown', (e) => {
    if (['input', 'textarea'].includes(document.activeElement.tagName.toLowerCase())) return;

    if (e.code === 'Space') {
      e.preventDefault();
      toggleCardFlip();
    } else if (e.code === 'ArrowRight') {
      nextCard();
    } else if (e.code === 'ArrowLeft') {
      prevCard();
    } else if (e.key === '1') {
      rateCard('hard');
    } else if (e.key === '2') {
      rateCard('med');
    } else if (e.key === '3') {
      rateCard('easy');
    }
  });

  renderCard();
}

function toggleCardFlip() {
  const cardBox = document.getElementById('flashcardBox');
  if (cardBox) {
    cardBox.classList.toggle('flipped');
  }
}

function renderCard() {
  const cardBox = document.getElementById('flashcardBox');
  if (cardBox) cardBox.classList.remove('flipped');

  if (!flashcardsData || flashcardsData.length === 0) {
    document.getElementById('cardQuestion').textContent = "No flashcards in this deck yet!";
    document.getElementById('cardAnswer').textContent = "Add your first card using the button above.";
    return;
  }

  const current = flashcardsData[currentIndex];
  document.getElementById('cardQuestion').textContent = current.question;
  document.getElementById('cardAnswer').textContent = current.answer;
  
  const hintEl = document.getElementById('cardHint');
  if (hintEl) {
    if (current.hint) {
      hintEl.textContent = `💡 Hint: ${current.hint}`;
      hintEl.style.display = 'inline-block';
    } else {
      hintEl.style.display = 'none';
    }
  }

  // Update Counters & Progress Bar
  const counterEl = document.getElementById('cardCounter');
  if (counterEl) {
    counterEl.textContent = `${currentIndex + 1} / ${flashcardsData.length}`;
  }

  const progressFill = document.getElementById('flashcardProgressFill');
  if (progressFill) {
    const pct = ((currentIndex + 1) / flashcardsData.length) * 100;
    progressFill.style.width = `${pct}%`;
  }
}

function nextCard() {
  if (currentIndex < flashcardsData.length - 1) {
    currentIndex++;
    renderCard();
  } else {
    showToast("🎉 You've reached the end of this deck! Review again or shuffle.", 'success');
  }
}

function prevCard() {
  if (currentIndex > 0) {
    currentIndex--;
    renderCard();
  }
}

function rateCard(rating) {
  if (rating === 'easy') cardStats.easy++;
  if (rating === 'med') cardStats.med++;
  if (rating === 'hard') cardStats.hard++;

  showToast(`Marked as ${rating.toUpperCase()}! Moving forward.`, 'info');
  nextCard();
}

function shuffleCards() {
  for (let i = flashcardsData.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [flashcardsData[i], flashcardsData[j]] = [flashcardsData[j], flashcardsData[i]];
  }
  currentIndex = 0;
  renderCard();
  showToast('Deck shuffled!', 'info');
}
