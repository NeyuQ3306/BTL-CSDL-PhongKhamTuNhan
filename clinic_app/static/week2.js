/* Progressive enhancement only. Server remains authoritative for every write. */
(() => {
  const form = document.querySelector('#clinical-form');
  if (!form) return;
  const get = id => document.getElementById(id);
  const mode = get('che_do_dot');
  if (mode) {
    const patient = get('ma_benh_nhan');
    const code = get('ma_dot');
    const picker = get('episode-picker');
    const options = Array.from(picker.options).slice(1).map(o => o.cloneNode(true));
    let newCode = mode.value === 'new' ? code.value : '';
    let previousMode = mode.value;
    function refresh(changedPatient = false) {
      const existing = mode.value === 'existing';
      const selected = changedPatient ? '' : code.value;
      if (previousMode === 'new' && existing) newCode = code.value;
      if (previousMode === 'existing' && !existing) code.value = newCode;
      const owner = patient ? patient.value : form.dataset.patient;
      picker.replaceChildren(new Option('— Chọn đợt —', ''));
      options.filter(o => o.dataset.patient === owner).forEach(o => picker.add(o.cloneNode(true)));
      picker.value = selected;
      get('episode-picker-wrap').hidden = !existing;
      picker.required = existing;
      picker.disabled = !existing;
      code.readOnly = existing;
      if (existing) {
        // Preserve a rejected POST code for inspection; a fresh patient choice clears it.
        if (changedPatient) code.value = '';
        else if (picker.value) code.value = picker.value;
        else if (previousMode === 'new') code.value = '';
      }
      form.querySelectorAll('[data-new-episode]').forEach(box => {
        box.hidden = existing;
        box.querySelectorAll('select').forEach(input => {
          input.disabled = existing;
          input.required = !existing;
        });
      });
      get('episode-info').textContent = !owner ? 'Chọn bệnh nhân trước.' :
        picker.options.length === 1 ? 'Bệnh nhân chưa có đợt đang điều trị. Chọn đợt mới nếu phù hợp.' :
        'Chỉ hiển thị đợt đang điều trị của bệnh nhân này. Bệnh và bác sĩ giữ nguyên theo đợt.';
      previousMode = mode.value;
    }
    mode.addEventListener('change', () => refresh());
    patient?.addEventListener('change', () => refresh(true));
    picker.addEventListener('change', () => { code.value = picker.value; });
    refresh();
  }
  if (form.dataset.action === 'support') {
    const records = JSON.parse(get('support-data').textContent);
    const nurse = get('ma_y_ta'), day = get('ngay_ho_tro'), content = get('noi_dung_ho_tro');
    const drafts = new Map();
    let previous = nurse.value;
    const blankDay = day.value;
    function load(initial = false) {
      if (!initial) drafts.set(previous, {day: day.value, content: content.value});
      const row = records.find(x => x.ma_y_ta === nurse.value);
      if (!(initial && form.dataset.posted === 'true')) {
        const draft = drafts.get(nurse.value);
        day.value = draft?.day || row?.ngay_ho_tro || blankDay;
        content.value = draft?.content ?? row?.noi_dung_ho_tro ?? '';
      }
      // A rejected date stays editable so the user can correct it.
      day.readOnly = Boolean(row && day.value === row.ngay_ho_tro);
      get('support-info').textContent = row ? 'Đã có hỗ trợ: giữ ngày bắt đầu, chỉ cập nhật nội dung.' :
        'Y tá mới: lưu để thêm người hỗ trợ cho lượt này.';
      previous = nurse.value;
    }
    nurse.addEventListener('change', () => load());
    load(true);
  }
  const box = get('medicine-lines');
  if (box) {
    const add = get('add-medicine'), status = get('medicine-status');
    function renumber() {
      Array.from(box.children).forEach((row, i) => {
        row.querySelector('legend').textContent = `Thuốc ${i + 1}`;
        row.querySelector('.remove-medicine').textContent = `Xóa dòng ${i + 1}`;
        row.querySelectorAll('input,select').forEach((input, j) => {
          input.id = `drug-${i}-${j}`;
          input.closest('div').querySelector('label').htmlFor = input.id;
        });
      });
      add.disabled = box.children.length >= 100;
    }
    function wire(row) {
      const remove = row.querySelector('.remove-medicine');
      remove.hidden = false;
      remove.addEventListener('click', () => {
        const next = row.nextElementSibling || row.previousElementSibling;
        if (box.children.length > 1) row.remove();
        else row.querySelectorAll('input,select').forEach(x => { x.value = ''; });
        renumber();
        (next?.querySelector('select') || add).focus();
        status.textContent = `Đã xóa dòng thuốc. Còn ${box.children.length} dòng.`;
      });
    }
    Array.from(box.children).forEach(wire);
    add.hidden = false;
    add.addEventListener('click', () => {
      if (box.children.length >= 100) return;
      const row = box.firstElementChild.cloneNode(true);
      row.querySelectorAll('input,select').forEach(x => { x.value = ''; });
      box.appendChild(row); wire(row); renumber();
      row.querySelector('select').focus();
      status.textContent = `Đã thêm dòng ${box.children.length}.`;
    });
    renumber();
  }
  // Focus the server error before the long form; values are never rewritten here.
  get('clinical-error')?.focus();
})();
