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
  const chart = panel.querySelector('#r01-chart');
  const legend = panel.querySelector('#r01-legend');
  const chartDetail = panel.querySelector('#r01-chart-detail');
  const chartScroll = panel.querySelector('#r01-chart-scroll');
  const chartEmpty = panel.querySelector('#r01-chart-empty');
  // Project-owned SVG renderer: no external library, font, asset or network request.
  const groups = [
    {id: 0, label: '0–5', color: '#2563a6'},
    {id: 1, label: '6–17', color: '#ad5710'},
    {id: 2, label: '18–59', color: '#087f72'},
    {id: 3, label: '60+', color: '#8052a0'},
    {id: -1, label: 'Ngày sinh không hợp lệ (nhóm riêng)', color: '#58616e'},
  ];
  const detailHint = 'Trỏ hoặc dùng Tab đến một phần cột để xem chi tiết.';

  function svgNode(name, attrs = {}, text) {
    const node = document.createElementNS('http://www.w3.org/2000/svg', name);
    Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, String(value)));
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function renderChart(data, period) {
    chart.replaceChildren();
    legend.replaceChildren();
    chartDetail.textContent = detailHint;
    panel.querySelector('#r01-chart-period').textContent = `Kỳ thực trả về: ${period}. Số dòng nguồn: ${data.row_count}. Đơn vị: đợt; số bệnh nhân trong chi tiết thuộc từng nhóm.`;
    chartEmpty.hidden = data.rows.length !== 0;
    chartScroll.hidden = data.rows.length === 0;
    chartDetail.hidden = data.rows.length === 0;
    if (!data.rows.length) return;
    const diseases = new Map();
    data.rows.forEach(row => {
      if (!diseases.has(row.ma_benh)) diseases.set(row.ma_benh, []);
      diseases.get(row.ma_benh).push(row);
    });
    const present = new Set(data.rows.map(row => row.thu_tu_nhom));
    groups.filter(group => present.has(group.id)).forEach(group => {
      const item = document.createElement('li');
      const swatch = document.createElement('span');
      swatch.className = 'analytics-swatch';
      swatch.style.backgroundColor = group.color;
      swatch.setAttribute('aria-hidden', 'true');
      if (group.id === -1) swatch.style.borderStyle = 'dashed';
      item.append(swatch, document.createTextNode(group.label));
      legend.append(item);
    });
    // Sum episodes for visual stacking only; never sum DISTINCT patients.
    const maximum = Math.max(1, ...Array.from(diseases.values(), rows => rows.reduce((n, row) => n + row.so_dot, 0)));
    const tickStep = Math.max(1, Math.ceil(maximum / 5));
    const axisMaximum = Math.ceil(maximum / tickStep) * tickStep;
    const width = Math.max(760, 110 + diseases.size * 76);
    const left = 80, top = 38, plotHeight = 290, baseline = top + plotHeight;
    const slot = (width - left - 24) / diseases.size;
    chart.setAttribute('viewBox', `0 0 ${width} 420`);
    chart.style.width = `${width}px`;
    chart.append(svgNode('title', {id: 'r01-svg-title'}, 'R01 — Số đợt theo bệnh và nhóm tuổi'));
    chart.append(svgNode('desc', {id: 'r01-svg-desc'}, `${period}. Cột chồng số đợt theo mã bệnh và nhóm tuổi từ cùng dữ liệu với bảng. Dùng Tab để xem số đợt và bệnh nhân từng nhóm; bảng bên dưới chứa đầy đủ tên bệnh và giá trị.`));
    chart.append(svgNode('text', {x: left, y: 20}, 'Số đợt'));
    for (let tick = 0; tick <= axisMaximum; tick += tickStep) {
      const y = baseline - tick / axisMaximum * plotHeight;
      chart.append(svgNode('line', {x1: left, x2: width - 24, y1: y, y2: y, stroke: '#dbe3e8'}));
      chart.append(svgNode('text', {x: left - 10, y: y + 4, 'text-anchor': 'end'}, tick));
    }
    let index = 0;
    diseases.forEach((rows, code) => {
      const x = left + slot * index + slot * 0.2;
      let stacked = 0;
      groups.forEach(group => {
        const row = rows.find(item => item.thu_tu_nhom === group.id);
        if (!row) return; // Missing groups remain absent, not fabricated zero rows.
        const height = row.so_dot / axisMaximum * plotHeight;
        stacked += row.so_dot;
        const detail = `${code} — ${row.ten_benh}; ${group.id === -1 ? group.label : `nhóm tuổi ${row.nhom_tuoi}`}: ${row.so_dot} đợt, ${row.so_benh_nhan} bệnh nhân trong nhóm.`;
        const rect = svgNode('rect', {x, y: baseline - stacked / axisMaximum * plotHeight, width: slot * 0.6, height,
          fill: group.color, class: 'chart-segment', tabindex: 0, role: 'img', 'aria-label': detail,
          'data-disease': code, 'data-age': group.id, 'data-episodes': row.so_dot, 'data-patients': row.so_benh_nhan});
        if (group.id === -1) rect.setAttribute('stroke-dasharray', '4 2');
        rect.append(svgNode('title', {}, detail));
        rect.addEventListener('mouseenter', () => { chartDetail.textContent = detail; });
        rect.addEventListener('focus', () => { chartDetail.textContent = detail; });
        chart.append(rect);
      });
      chart.append(svgNode('text', {x: x + slot * 0.3, y: baseline + 24, 'text-anchor': 'middle'}, code));
      index += 1;
    });
    chart.append(svgNode('text', {x: left + (width - left) / 2, y: 395, 'text-anchor': 'middle'}, 'Bệnh (mã bệnh; tên đầy đủ trong bảng và chi tiết)'));
  }
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
    chart.replaceChildren();
    legend.replaceChildren();
    chartDetail.textContent = detailHint;
    error.hidden = true;
    panel.setAttribute('aria-busy', 'false');
  }

  function validate(data, params) {
    const age = params.get('age_group');
    const keys = new Set();
    if (!data || data.report_id !== 'R01' || data.interval !== 'end_exclusive' ||
        !Array.isArray(data.rows) || data.row_count !== data.rows.length ||
        typeof data.data_notice !== 'string' ||
        data.filters?.start !== params.get('start') || data.filters?.end !== params.get('end') ||
        (age === null ? data.filters?.age_group !== undefined : data.filters?.age_group !== Number(age)) ||
        !data.rows.every(row => row && typeof row.ma_benh === 'string' && typeof row.ten_benh === 'string' &&
          typeof row.nhom_tuoi === 'string' && [-1, 0, 1, 2, 3].includes(row.thu_tu_nhom) &&
          Number.isSafeInteger(row.so_dot) && row.so_dot >= 0 &&
          Number.isSafeInteger(row.so_benh_nhan) && row.so_benh_nhan >= 0 &&
          (age === null || row.thu_tu_nhom === Number(age)) &&
          !keys.has(JSON.stringify([row.ma_benh, row.thu_tu_nhom])) &&
          keys.add(JSON.stringify([row.ma_benh, row.thu_tu_nhom])))) {
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
      renderChart(data, `${period}. ${group}`);
      panel.querySelector('#analytics-applied').textContent = `Kỳ thực trả về: ${period}. ${group}. Số dòng: ${data.row_count} (không phải tổng bệnh nhân).`;
      panel.querySelector('#analytics-caption').textContent = `R01 — Bệnh theo nhóm tuổi · ${period} · ${group}`;
      panel.querySelector('#analytics-data-notice').textContent = data.data_notice;
      result.hidden = false;
      status.textContent = data.rows.length ? `Đã tải ${data.row_count} dòng R01.` : 'Đã tải R01: không có dữ liệu phù hợp.';
    } catch (exc) {
      if (current !== generation) return;
      result.hidden = true;
      body.replaceChildren();
      chart.replaceChildren();
      legend.replaceChildren();
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
