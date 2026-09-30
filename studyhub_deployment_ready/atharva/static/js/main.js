// ===================================================================
// StudyHub - Main JavaScript
// ===================================================================

document.addEventListener('DOMContentLoaded', () => {
  initThemeToggle();
  initMobileMenu();
  initBookmarks();
  initUpvotes();
});

// Theme Toggle (Dark / Light)
function initThemeToggle() {
  const toggleBtn = document.getElementById('themeToggleBtn');
  const currentTheme = localStorage.getItem('studyhub_theme') || 'light';
  
  document.documentElement.setAttribute('data-theme', currentTheme);
  updateThemeIcon(currentTheme);

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const activeTheme = document.documentElement.getAttribute('data-theme');
      const newTheme = activeTheme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('studyhub_theme', newTheme);
      updateThemeIcon(newTheme);
      showToast(`Switched to ${newTheme} mode`, 'info');
    });
  }
}

function updateThemeIcon(theme) {
  const toggleBtn = document.getElementById('themeToggleBtn');
  if (!toggleBtn) return;
  toggleBtn.innerHTML = theme === 'dark' 
    ? '<i class="bi bi-sun-fill" style="color: #fbbf24;"></i>' 
    : '<i class="bi bi-moon-stars-fill" style="color: #6366f1;"></i>';
}

// Mobile Navbar Toggle
function initMobileMenu() {
  const menuToggle = document.getElementById('mobileMenuToggle');
  const navLinks = document.getElementById('navLinks');
  if (menuToggle && navLinks) {
    menuToggle.addEventListener('click', () => {
      navLinks.classList.toggle('mobile-open');
    });
  }
}

// Toast Notifications
function showToast(message, type = 'info') {
  let toastContainer = document.getElementById('toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 10000;
      display: flex;
      flex-direction: column;
      gap: 10px;
      pointer-events: none;
    `;
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement('div');
  toast.className = `flash-message flash-${type}`;
  toast.style.cssText = `
    min-width: 280px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    pointer-events: auto;
    cursor: pointer;
  `;
  toast.innerHTML = `
    <span>${message}</span>
    <span style="margin-left: 12px; font-weight: bold; cursor: pointer;">&times;</span>
  `;

  toast.addEventListener('click', () => toast.remove());
  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-10px)';
    setTimeout(() => toast.remove(), 400);
  }, 3500);
}

// Bookmark Toggle Handler
function initBookmarks() {
  document.querySelectorAll('.btn-bookmark-toggle').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      const resId = btn.getAttribute('data-resource-id');
      try {
        const resp = await fetch(`/api/resources/${resId}/bookmark`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        const data = await resp.json();
        if (data.success) {
          if (data.is_bookmarked) {
            btn.innerHTML = '<i class="bi bi-bookmark-fill" style="color: #4f46e5;"></i> Saved';
            showToast('Resource saved to your bookmarks!', 'success');
          } else {
            btn.innerHTML = '<i class="bi bi-bookmark"></i> Save';
            showToast('Removed from bookmarks', 'info');
          }
        } else {
          showToast(data.message || 'Please log in to bookmark.', 'error');
        }
      } catch (err) {
        showToast('Could not update bookmark', 'error');
      }
    });
  });
}

// Upvote Handler
function initUpvotes() {
  document.querySelectorAll('.btn-upvote').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      const topicId = btn.getAttribute('data-topic-id');
      try {
        const resp = await fetch(`/api/community/${topicId}/upvote`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        const data = await resp.json();
        if (data.success) {
          const countSpan = btn.querySelector('.upvote-count');
          if (countSpan) {
            countSpan.textContent = parseInt(countSpan.textContent || '0') + 1;
          }
          btn.style.color = '#4f46e5';
          btn.disabled = true;
          showToast('Upvote recorded! Thank you.', 'success');
        }
      } catch (err) {
        console.error(err);
      }
    });
  });
}
