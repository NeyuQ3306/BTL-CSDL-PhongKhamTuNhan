/* Application-owned reveal controls, independent of browser password widgets. */
(() => {
  'use strict';
  const controls = [];
  document.querySelectorAll('[data-password-field]').forEach(field => {
    const input = field.querySelector('input');
    const button = field.querySelector('.password-toggle');
    const label = field.querySelector('[data-password-label]');
    if (!input || !button || !label || field.classList.contains('is-enhanced')) return;
    const conceal = () => {
      input.type = 'password';
      button.setAttribute('aria-pressed', 'false');
      button.setAttribute('aria-label', 'Hiện mật khẩu');
      label.textContent = 'Hiện';
    };
    button.addEventListener('click', () => {
      const show = input.type === 'password';
      const start = input.selectionStart;
      const end = input.selectionEnd;
      input.type = show ? 'text' : 'password';
      button.setAttribute('aria-pressed', String(show));
      button.setAttribute('aria-label', show ? 'Ẩn mật khẩu' : 'Hiện mật khẩu');
      label.textContent = show ? 'Ẩn' : 'Hiện';
      // Preserve the caret without moving keyboard focus away from the button.
      if (start !== null && end !== null) input.setSelectionRange(start, end);
    });
    input.addEventListener('input', () => { if (!input.value) conceal(); });
    if (input.form) {
      input.form.addEventListener('submit', conceal);
      input.form.addEventListener('reset', conceal);
    }
    conceal();
    field.classList.add('is-enhanced');
    button.hidden = false;
    controls.push(conceal);
  });
  const concealAll = () => controls.forEach(conceal => conceal());
  window.addEventListener('pagehide', concealAll);
  window.addEventListener('pageshow', concealAll);
  document.addEventListener('visibilitychange', () => { if (document.hidden) concealAll(); });
})();
