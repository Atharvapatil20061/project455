// ===================================================================
// StudyHub - AI Study Assistant (EduBot) Widget
// ===================================================================

document.addEventListener('DOMContentLoaded', () => {
  initEduBot();
});

function initEduBot() {
  const toggleBtn = document.getElementById('edubotToggleBtn');
  const drawer = document.getElementById('edubotDrawer');
  const closeBtn = document.getElementById('edubotCloseBtn');
  const form = document.getElementById('edubotForm');
  const input = document.getElementById('edubotInput');
  const chatHistory = document.getElementById('edubotChatHistory');

  if (!toggleBtn || !drawer) return;

  toggleBtn.addEventListener('click', () => {
    drawer.classList.toggle('active');
    if (drawer.classList.contains('active')) {
      input.focus();
    }
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      drawer.classList.remove('active');
    });
  }

  // Quick suggestion chips
  document.querySelectorAll('.ai-prompt-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const prompt = chip.getAttribute('data-prompt');
      input.value = prompt;
      form.dispatchEvent(new Event('submit'));
    });
  });

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const query = input.value.trim();
      if (!query) return;

      appendEduBotMsg(query, 'user');
      input.value = '';

      // Show typing indicator
      const typingEl = document.createElement('div');
      typingEl.className = 'edubot-msg edubot-msg-bot';
      typingEl.id = 'edubotTyping';
      typingEl.innerHTML = '<em>EduBot is formulating an explanation...</em>';
      chatHistory.appendChild(typingEl);
      chatHistory.scrollTop = chatHistory.scrollHeight;

      try {
        const resp = await fetch('/api/ai/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: query })
        });
        const data = await resp.json();

        const indicator = document.getElementById('edubotTyping');
        if (indicator) indicator.remove();

        appendEduBotMsg(data.answer, 'bot');
      } catch (err) {
        const indicator = document.getElementById('edubotTyping');
        if (indicator) indicator.remove();
        appendEduBotMsg('Sorry, I encountered an issue connecting to the study brain. Please try again.', 'bot');
      }
    });
  }
}

function appendEduBotMsg(text, sender) {
  const chatHistory = document.getElementById('edubotChatHistory');
  if (!chatHistory) return;

  const msgDiv = document.createElement('div');
  msgDiv.className = `edubot-msg edubot-msg-${sender}`;

  if (sender === 'bot') {
    msgDiv.innerHTML = formatMarkdown(text);
  } else {
    msgDiv.textContent = text;
  }

  chatHistory.appendChild(msgDiv);
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

function formatMarkdown(text) {
  // Simple markdown processor for bold, code blocks, bullet points, headers
  let html = text
    .replace(/```python([\s\S]*?)```/g, '<pre style="background: rgba(0,0,0,0.15); padding: 8px; border-radius: 6px; font-family: monospace; overflow-x: auto; margin: 6px 0;"><code>$1</code></pre>')
    .replace(/```([\s\S]*?)```/g, '<pre style="background: rgba(0,0,0,0.15); padding: 8px; border-radius: 6px; font-family: monospace; overflow-x: auto; margin: 6px 0;"><code>$1</code></pre>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code style="background: rgba(79,70,229,0.1); padding: 2px 4px; border-radius: 4px; font-family: monospace;">$1</code>')
    .replace(/\n\n/g, '<br><br>')
    .replace(/\n- /g, '<br>• ');

  return html;
}
