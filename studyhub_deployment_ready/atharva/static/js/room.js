// ===================================================================
// StudyHub - Virtual Room & Whiteboard Engine
// ===================================================================

let canvas, ctx;
let isDrawing = false;
let currentColor = '#4f46e5';
let currentBrushSize = 3;
let isEraser = false;
let currentRoomId = null;
let chatPollInterval = null;

function initRoom(roomId) {
  currentRoomId = roomId;
  initWhiteboard();
  initRoomChat();
}

function initWhiteboard() {
  canvas = document.getElementById('whiteboardCanvas');
  if (!canvas) return;

  ctx = canvas.getContext('2d');
  resizeCanvas();

  window.addEventListener('resize', resizeCanvas);

  // Drawing event listeners (Mouse)
  canvas.addEventListener('mousedown', startDrawing);
  canvas.addEventListener('mousemove', draw);
  canvas.addEventListener('mouseup', stopDrawing);
  canvas.addEventListener('mouseleave', stopDrawing);

  // Touch Support for tablets and phones
  canvas.addEventListener('touchstart', (e) => {
    e.preventDefault();
    const touch = e.touches[0];
    const mouseEvent = new MouseEvent('mousedown', {
      clientX: touch.clientX,
      clientY: touch.clientY
    });
    canvas.dispatchEvent(mouseEvent);
  });

  canvas.addEventListener('touchmove', (e) => {
    e.preventDefault();
    const touch = e.touches[0];
    const mouseEvent = new MouseEvent('mousemove', {
      clientX: touch.clientX,
      clientY: touch.clientY
    });
    canvas.dispatchEvent(mouseEvent);
  });

  canvas.addEventListener('touchend', (e) => {
    e.preventDefault();
    const mouseEvent = new MouseEvent('mouseup', {});
    canvas.dispatchEvent(mouseEvent);
  });

  // Toolbar Tools
  document.getElementById('toolPencil').addEventListener('click', () => {
    isEraser = false;
    setActiveTool('toolPencil');
  });

  document.getElementById('toolEraser').addEventListener('click', () => {
    isEraser = true;
    setActiveTool('toolEraser');
  });

  document.getElementById('toolClear').addEventListener('click', () => {
    if (confirm('Clear the entire whiteboard?')) {
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      showToast('Whiteboard cleared', 'info');
    }
  });

  document.getElementById('toolDownload').addEventListener('click', () => {
    const link = document.createElement('a');
    link.download = `studyhub_whiteboard_room_${currentRoomId}.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
    showToast('Whiteboard saved as image!', 'success');
  });

  // Brush Size
  const sizeSelect = document.getElementById('brushSizeSelect');
  if (sizeSelect) {
    sizeSelect.addEventListener('change', (e) => {
      currentBrushSize = parseInt(e.target.value);
    });
  }

  // Color Swatches
  document.querySelectorAll('.color-dot').forEach(dot => {
    dot.addEventListener('click', () => {
      document.querySelectorAll('.color-dot').forEach(d => d.classList.remove('active'));
      dot.classList.add('active');
      currentColor = dot.getAttribute('data-color');
      isEraser = false;
      setActiveTool('toolPencil');
    });
  });
}

function resizeCanvas() {
  if (!canvas) return;
  const parent = canvas.parentElement;
  
  // Save current image before resizing to prevent clear
  const tempCanvas = document.createElement('canvas');
  tempCanvas.width = canvas.width;
  tempCanvas.height = canvas.height;
  const tempCtx = tempCanvas.getContext('2d');
  tempCtx.drawImage(canvas, 0, 0);

  canvas.width = parent.clientWidth;
  canvas.height = parent.clientHeight - 50;

  // Background white
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Restore previous drawing
  if (tempCanvas.width > 0) {
    ctx.drawImage(tempCanvas, 0, 0);
  }
}

function setActiveTool(toolId) {
  document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
  const btn = document.getElementById(toolId);
  if (btn) btn.classList.add('active');
}

function startDrawing(e) {
  isDrawing = true;
  draw(e);
}

function draw(e) {
  if (!isDrawing) return;

  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;

  ctx.lineWidth = isEraser ? currentBrushSize * 4 : currentBrushSize;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';

  if (isEraser) {
    ctx.strokeStyle = '#ffffff';
  } else {
    ctx.strokeStyle = currentColor;
  }

  ctx.lineTo(x, y);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(x, y);
}

function stopDrawing() {
  if (!isDrawing) return;
  isDrawing = false;
  ctx.beginPath();
}

// ----------------- Room Live Chat -----------------
function initRoomChat() {
  const form = document.getElementById('roomChatForm');
  const input = document.getElementById('roomChatInput');
  const messagesBox = document.getElementById('roomMessagesBox');

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;

      input.value = '';
      try {
        await fetch(`/api/room/${currentRoomId}/messages`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text })
        });
        fetchRoomMessages();
      } catch (err) {
        console.error(err);
      }
    });
  }

  // Scroll to bottom
  if (messagesBox) {
    messagesBox.scrollTop = messagesBox.scrollHeight;
  }

  // Poll for new messages every 3.5 seconds
  chatPollInterval = setInterval(fetchRoomMessages, 3500);
}

async function fetchRoomMessages() {
  try {
    const resp = await fetch(`/api/room/${currentRoomId}/messages`);
    const data = await resp.json();
    if (data.messages) {
      renderRoomMessages(data.messages);
    }
  } catch (err) {
    console.error('Chat poll error:', err);
  }
}

function renderRoomMessages(messages) {
  const box = document.getElementById('roomMessagesBox');
  if (!box) return;

  const isScrolledToBottom = box.scrollHeight - box.clientHeight <= box.scrollTop + 50;

  box.innerHTML = '';
  messages.forEach(m => {
    const item = document.createElement('div');
    item.className = 'room-message-item';
    item.innerHTML = `
      <div class="avatar-circle" style="width: 28px; height: 28px; font-size: 0.75rem; flex-shrink: 0;">
        ${m.username.charAt(0).toUpperCase()}
      </div>
      <div class="message-bubble">
        <div class="message-sender">${m.username}</div>
        <div>${escapeHtml(m.message)}</div>
      </div>
    `;
    box.appendChild(item);
  });

  if (isScrolledToBottom) {
    box.scrollTop = box.scrollHeight;
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
