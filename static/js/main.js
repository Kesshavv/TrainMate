// TrainMate — main.js

// Auto-dismiss flash messages after 4 seconds
document.addEventListener('DOMContentLoaded', () => {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(f => {
    setTimeout(() => {
      f.style.opacity = '0';
      f.style.transition = 'opacity .4s';
      setTimeout(() => f.remove(), 400);
    }, 4000);
  });

  // Mobile sidebar — close on backdrop click
  document.addEventListener('click', (e) => {
    const sidebar = document.getElementById('sidebar');
    const toggle  = document.querySelector('.menu-toggle');
    if (sidebar && sidebar.classList.contains('open') && !sidebar.contains(e.target) && e.target !== toggle) {
      sidebar.classList.remove('open');
    }
  });

  // Active nav highlight (already handled by Jinja, but keep JS fallback)
  const links = document.querySelectorAll('.nav-link');
  links.forEach(l => {
    if (l.href === window.location.href) l.classList.add('active');
  });

  // Animate stat numbers on load
  document.querySelectorAll('.stat-value').forEach(el => {
    const text = el.textContent.trim();
    const num  = parseFloat(text.replace(/[^0-9.]/g, ''));
    if (!isNaN(num) && num > 0 && num < 100000) {
      let start = 0;
      const step = num / 30;
      const timer = setInterval(() => {
        start += step;
        if (start >= num) { start = num; clearInterval(timer); }
        el.textContent = text.includes('.') ? start.toFixed(1) : Math.round(start);
      }, 25);
    }
  });
});
