/* R01 presentation adapter. Business counts and ordering come from the API. */
(() => {
  'use strict';
  const panel = document.querySelector('#analytics');
  if (!panel) return;
  const form = panel.querySelector('form');
  const status = panel.querySelector('#analytics-status');
  const error = panel.querySelector('#analytics-error');
  const result = panel.querySelector('#analytics-result');
  const body = panel.querySelector('tbody');
  const fields = ['ma_benh', 'ten_benh', 'thu_tu_nhom', 'nhom_tuoi', 'so_dot', 'so_benh_nhan'];
  let generation = 0;
  let controller;

  function parseDate(value) {
    if (!/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(value) || value < '0001-01-01') throw new Error('Chọn ngày hợp lệ, dạng YYYY-MM-DD.');
    const [year, month, day] = value.split('-').map(Number);
    const date = new Date(0);
    date.setUTCHours(0, 0, 0, 0);
    date.setUTCFullYear(year, month - 1, day);
    if (date.toISOString().slice(0, 10) !== value) throw new Error('Ngày không hợp lệ theo lịch.');
    return date;
  }

  function query() {
    const start = form.elements.start.value;
    const through = form.elements.through.value;
    parseDate(start);
    const end = parseDate(through);
    if (through > '9999-12-30') throw new Error('Ngày cuối bao gồm tối đa là 30/12/9999.');
    if (start > through) throw new Error('Từ ngày phải trước hoặc bằng ngày cuối.');
    // Always advance the original form value once, using calendar days in UTC.
    end.setUTCDate(end.getUTCDate() + 1);
    const params = new URLSearchParams({start, end: end.toISOString().slice(0, 10)});
    const age = form.elements.age_group.value;
    if (age !== '') {
      if (!['-1', '0', '1', '2', '3'].includes(age)) throw new Error('Nhóm tuổi không hợp lệ.');
      params.set('age_group', age);
    }
    return params;
  }

  function clear() {
    generation += 1;
    if (controller) controller.abort();
    result.hidden = true;
    body.replaceChildren();
    error.hidden = true;
    panel.setAttribute('aria-busy', 'false');
  }

  function validate(data, params) {
    const age = params.get('age_group');
    if (data.report_id !== 'R01' || data.interval !== 'end_exclusive' ||
        !Array.isArray(data.rows) || data.row_count !== data.rows.length ||
        typeof data.data_notice !== 'string' ||
        data.filters?.start !== params.get('start') || data.filters?.end !== params.get('end') ||
        (age === null ? data.filters?.age_group !== undefined : data.filters?.age_group !== Number(age)) ||
        !data.rows.every(row => row && typeof row.ma_benh === 'string' && typeof row.ten_benh === 'string' &&
          typeof row.nhom_tuoi === 'string' && [-1, 0, 1, 2, 3].includes(row.thu_tu_nhom) &&
          Number.isSafeInteger(row.so_dot) && row.so_dot >= 0 &&
          Number.isSafeInteger(row.so_benh_nhan) && row.so_benh_nhan >= 0)) {
      throw new Error('Dữ liệu trả về không đúng hợp đồng R01. Chưa thể hiển thị bảng.');
    }
  }

  form.addEventListener('input', () => {
    clear();
    status.textContent = 'Bộ lọc đã đổi. Bấm Xem R01 để tải kết quả tương ứng.';
  });
  form.addEventListener('submit', async event => {
    event.preventDefault();
    clear();
    const current = generation;
    let timer;
    let timedOut = false;
    try {
      const params = query();
      controller = new AbortController();
      const requestController = controller;
      timer = setTimeout(() => { timedOut = true; requestController.abort(); }, 20000);
      panel.setAttribute('aria-busy', 'true');
      status.textContent = 'Đang tải R01…';
      const response = await fetch(`${panel.dataset.endpoint}?${params}`, {signal: controller.signal, headers: {Accept: 'application/json'}});
      if (current !== generation) return;
      if (!response.ok) {
        const messages = {400: 'Bộ lọc bị API từ chối. Kiểm tra ngày và nhóm tuổi.', 404: 'Không tìm thấy API R01.', 500: 'Máy chủ chưa xử lý được báo cáo.', 503: 'Chưa kết nối được MySQL. Kiểm tra kết nối rồi thử lại.'};
        throw new Error(`Lỗi ${response.status}: ${messages[response.status] || 'Không thể tải báo cáo.'}`);
      }
      const data = await response.json();
      if (current !== generation) return;
      validate(data, params);
      const fragment = document.createDocumentFragment();
      for (const row of data.rows) {
        const tr = document.createElement('tr');
        fields.forEach((key, index) => {
          const cell = document.createElement(index === 0 ? 'th' : 'td');
          if (index === 0) cell.scope = 'row';
          cell.textContent = String(row[key]);
          tr.append(cell);
        });
        fragment.append(tr);
      }
      if (!data.rows.length) {
        const tr = document.createElement('tr');
        const cell = document.createElement('td');
        cell.colSpan = fields.length;
        cell.textContent = 'Không có dữ liệu phù hợp bộ lọc.';
        tr.append(cell); fragment.append(tr);
      }
      body.replaceChildren(fragment);
      const group = data.filters.age_group === undefined ? 'Tất cả nhóm' : `Nhóm ${data.filters.age_group}`;
      const period = `${data.filters.start} ≤ ngày khám < ${data.filters.end}`;
      panel.querySelector('#analytics-applied').textContent = `Kỳ thực trả về: ${period}. ${group}. Số dòng: ${data.row_count} (không phải tổng bệnh nhân).`;
      panel.querySelector('#analytics-caption').textContent = `R01 — Bệnh theo nhóm tuổi · ${period} · ${group}`;
      panel.querySelector('#analytics-data-notice').textContent = data.data_notice;
      result.hidden = false;
      status.textContent = data.rows.length ? `Đã tải ${data.row_count} dòng R01.` : 'Đã tải R01: không có dữ liệu phù hợp.';
    } catch (exc) {
      if (current !== generation) return;
      result.hidden = true;
      body.replaceChildren();
      status.textContent = 'Chưa có kết quả cho bộ lọc này.';
      error.textContent = timedOut ? 'Tải báo cáo quá lâu. Kiểm tra kết nối rồi thử lại.' :
        exc.name === 'TypeError' ? 'Không thể kết nối đến API. Kiểm tra kết nối rồi thử lại.' : exc.message;
      error.hidden = false;
    } finally {
      clearTimeout(timer);
      if (current === generation) panel.setAttribute('aria-busy', 'false');
    }
  });
})();
