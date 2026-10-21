/* Localize numeric browser validation without changing native/server constraints. */
(() => {
  const localized = new WeakSet();
  const isNumber = input => input instanceof HTMLInputElement && input.type === 'number';
  function clear(input) {
    if (!localized.has(input)) return;
    input.setCustomValidity('');
    localized.delete(input);
  }
  // Capture also covers medicine rows added after the page was loaded.
  document.addEventListener('invalid', event => {
    const input = event.target;
    if (!isNumber(input)) return;
    clear(input);
    // Preserve validation messages installed by other enhancements.
    if (input.validity.customError) return;
    const validity = input.validity;
    let message = '';
    if (validity.badInput) message = 'Vui lòng nhập một số hợp lệ.';
    else if (validity.valueMissing) message = 'Vui lòng nhập số vào ô này.';
    else if (validity.rangeUnderflow) message = `Giá trị phải lớn hơn hoặc bằng ${input.min}.`;
    else if (validity.rangeOverflow) message = `Giá trị không được lớn hơn ${input.max}.`;
    else if (validity.stepMismatch) message = input.step === '1' ?
      'Vui lòng nhập số nguyên.' : 'Vui lòng nhập số theo bước hợp lệ.';
    if (message) {
      input.setCustomValidity(message);
      localized.add(input);
    }
  }, true);
  document.addEventListener('input', event => {
    if (isNumber(event.target)) clear(event.target);
  });
  document.addEventListener('change', event => {
    if (isNumber(event.target)) clear(event.target);
  });
})();
