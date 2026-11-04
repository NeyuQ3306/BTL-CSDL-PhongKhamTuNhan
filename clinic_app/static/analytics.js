/* R01–R03 presentation adapters. Counts and ordering come from the same API response. */
(() => {
  'use strict';
  const panel = document.querySelector('#analytics');
  if (!panel) return;
  const form = panel.querySelector('form');
  const status = panel.querySelector('#analytics-status');
  const error = panel.querySelector('#analytics-error');
  const result = panel.querySelector('#analytics-result');
  const body = panel.querySelector('tbody');
  const reports = {
    R01: {title: 'Bệnh theo nhóm tuổi', fields: ['ma_benh', 'ten_benh', 'thu_tu_nhom', 'nhom_tuoi', 'so_dot', 'so_benh_nhan'],
      headers: ['Mã bệnh', 'Tên bệnh', 'Mã nhóm', 'Nhóm tuổi', 'Số đợt', 'Số bệnh nhân']},
    R02: {title: 'Tiếp nhận và khám theo ngày', fields: ['ngay', 'so_luot', 'so_benh_nhan_tiep_nhan', 'so_lan_kham'],
      headers: ['Ngày', 'Lượt tiếp nhận (lượt)', 'Bệnh nhân tiếp nhận (người/ngày)', 'Lần khám (lần)']},
    R03: {title: 'Khối lượng khám theo bác sĩ', fields: ['ma_bac_si', 'ho_ten', 'chuyen_mon', 'so_lan_kham', 'so_dot', 'so_benh_nhan'],
      headers: ['Mã bác sĩ', 'Họ tên', 'Chuyên môn', 'Lần khám (lần)', 'Đợt điều trị (đợt)', 'Bệnh nhân (người)']},
  };
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
  const r02Chart = panel.querySelector('#r02-chart');
  const r02Detail = panel.querySelector('#r02-chart-detail');
  const r03Chart = panel.querySelector('#r03-chart');
  const r03Detail = panel.querySelector('#r03-chart-detail');

  function selectReport() {
    const id = form.elements.report.value;
    const isR01 = id === 'R01';
    panel.querySelector('#analytics-age-field').hidden = !isR01;
    form.elements.age_group.disabled = !isR01;
    Object.keys(reports).forEach(report => {
      const prefix = report.toLowerCase();
      panel.querySelector(`#${prefix}-description`).hidden = report !== id;
      panel.querySelector(`#${prefix}-chart-section`).hidden = report !== id;
    });
    form.querySelector('button').textContent = `Xem ${id}`;
  }

  function renderR03(data, period) {
    r03Chart.replaceChildren();
    r03Detail.textContent = 'Trỏ hoặc dùng Tab đến một thanh để xem chi tiết.';
    panel.querySelector('#r03-chart-period').textContent = `Kỳ thực trả về: ${period}. Số bác sĩ trả về: ${data.row_count}. Không loại bác sĩ có 0 hoạt động. Đơn vị thanh: lần khám; số đợt và bệnh nhân riêng trong bảng/chi tiết.`;
    panel.querySelector('#r03-chart-empty').hidden = data.rows.length !== 0;
    panel.querySelector('#r03-chart-scroll').hidden = data.rows.length === 0;
    r03Detail.hidden = data.rows.length === 0;
    if (!data.rows.length) return;
    const maximum = data.rows.reduce((n, row) => Math.max(n, row.so_lan_kham), 1);
    const step = Math.max(1, Math.ceil(maximum / 5));
    const axisMaximum = Math.ceil(maximum / step) * step;
    const width = 960, left = 250, plotWidth = 620, top = 50, rowHeight = 56;
    const bottom = top + data.rows.length * rowHeight;
    const height = bottom + 70;
    r03Chart.setAttribute('viewBox', `0 0 ${width} ${height}`);
    r03Chart.style.width = `${width}px`;
    r03Chart.style.height = `${height}px`;
    r03Chart.append(svgNode('title', {id: 'r03-svg-title'}, 'R03 — Khối lượng khám theo bác sĩ'));
    r03Chart.append(svgNode('desc', {id: 'r03-svg-desc'}, `${period}. Thanh ngang là số lần khám, giữ bác sĩ 0 hoạt động và thứ tự API. Không xếp hạng chất lượng. Tên đầy đủ, chuyên môn, số đợt và bệnh nhân có trong chi tiết và bảng.`));
    r03Chart.append(svgNode('text', {x: 20, y: 24}, 'Bác sĩ (mã / họ tên)'));
    for (let tick = 0; tick <= axisMaximum; tick += step) {
      const x = left + tick / axisMaximum * plotWidth;
      r03Chart.append(svgNode('line', {x1: x, x2: x, y1: top - 10, y2: bottom, stroke: '#dbe3e8'}));
      r03Chart.append(svgNode('text', {x, y: bottom + 24, 'text-anchor': 'middle'}, tick));
    }
    data.rows.forEach((row, index) => {
      const y = top + index * rowHeight;
      const detail = `${row.ma_bac_si} — ${row.ho_ten}; chuyên môn: ${row.chuyen_mon}; ${row.so_lan_kham} lần khám, ${row.so_dot} đợt điều trị, ${row.so_benh_nhan} bệnh nhân khác nhau của bác sĩ trong kỳ. Không đánh giá chất lượng bác sĩ.`;
      r03Chart.append(svgNode('text', {x: left - 16, y: y + 10, 'text-anchor': 'end'}, row.ma_bac_si));
      const shortName = Array.from(row.ho_ten).slice(0, 27).join('');
      const label = svgNode('text', {x: left - 16, y: y + 30, 'text-anchor': 'end'}, shortName + (shortName === row.ho_ten ? '' : '…'));
      label.append(svgNode('title', {}, row.ho_ten));
      r03Chart.append(label);
      const length = row.so_lan_kham / axisMaximum * plotWidth;
      const rect = svgNode('rect', {x: left, y, width: length, height: 34, fill: '#2563a6',
        class: 'chart-segment', tabindex: 0, role: 'img', 'aria-label': detail,
        'data-doctor': row.ma_bac_si, 'data-examinations': row.so_lan_kham,
        'data-episodes': row.so_dot, 'data-patients': row.so_benh_nhan});
      rect.append(svgNode('title', {}, detail));
      rect.addEventListener('mouseenter', () => { r03Detail.textContent = detail; });
      rect.addEventListener('focus', () => { r03Detail.textContent = detail; });
      r03Chart.append(rect);
      r03Chart.append(svgNode('text', {x: left + length + 8, y: y + 23}, row.so_lan_kham));
    });
    r03Chart.append(svgNode('text', {x: left + plotWidth / 2, y: height - 12, 'text-anchor': 'middle'}, 'Số lần khám (lần)'));
  }

  function renderR02(data, period) {
    r02Chart.replaceChildren();
    r02Detail.textContent = 'Trỏ hoặc dùng Tab đến một cột để xem chi tiết.';
    panel.querySelector('#r02-chart-period').textContent = `Kỳ thực trả về: ${period}. Số ngày có bản ghi trả về: ${data.row_count}. Đơn vị cột: lượt tiếp nhận / lần khám; bệnh nhân tiếp nhận (người/ngày) trong bảng và chi tiết.`;
    panel.querySelector('#r02-chart-empty').hidden = data.rows.length !== 0;
    panel.querySelector('#r02-chart-scroll').hidden = data.rows.length === 0;
    r02Detail.hidden = data.rows.length === 0;
    if (!data.rows.length) return;
    const maximum = data.rows.reduce((n, row) => Math.max(n, row.so_luot, row.so_lan_kham), 1);
    const step = Math.max(1, Math.ceil(maximum / 5));
    const axisMaximum = Math.ceil(maximum / step) * step;
    const width = Math.max(760, 110 + data.rows.length * 100);
    const left = 80, baseline = 328, plotHeight = 290;
    const slot = (width - left - 24) / data.rows.length;
    r02Chart.setAttribute('viewBox', `0 0 ${width} 460`);
    r02Chart.style.width = `${width}px`;
    r02Chart.append(svgNode('title', {id: 'r02-svg-title'}, 'R02 — Tiếp nhận và khám theo ngày'));
    r02Chart.append(svgNode('desc', {id: 'r02-svg-desc'}, `${period}. Hai cột riêng: lượt tiếp nhận và lần khám cho từng ngày API trả về. Không chèn ngày thiếu. Bệnh nhân tiếp nhận trong chi tiết là số người khác nhau trong ngày.`));
    r02Chart.append(svgNode('text', {x: left, y: 20}, 'Số lượt / số lần khám'));
    for (let tick = 0; tick <= axisMaximum; tick += step) {
      const y = baseline - tick / axisMaximum * plotHeight;
      r02Chart.append(svgNode('line', {x1: left, x2: width - 24, y1: y, y2: y, stroke: '#dbe3e8'}));
      r02Chart.append(svgNode('text', {x: left - 10, y: y + 4, 'text-anchor': 'end'}, tick));
    }
    data.rows.forEach((row, index) => {
      const x = left + index * slot;
      const detail = `${row.ngay}: ${row.so_luot} lượt tiếp nhận; ${row.so_lan_kham} lần khám; ${row.so_benh_nhan_tiep_nhan} bệnh nhân tiếp nhận (người khác nhau trong ngày).`;
      [['so_luot', '#2563a6', 'Lượt tiếp nhận'], ['so_lan_kham', '#ad5710', 'Lần khám']].forEach(([key, color, label], series) => {
        const height = row[key] / axisMaximum * plotHeight;
        const rect = svgNode('rect', {x: x + slot * (0.15 + series * 0.32), y: baseline - height,
          width: slot * 0.28, height, fill: color, class: 'chart-segment', tabindex: 0, role: 'img',
          'aria-label': `${label}. ${detail}`, 'data-date': row.ngay, 'data-series': key,
          'data-count': row[key], 'data-patients': row.so_benh_nhan_tiep_nhan});
        rect.append(svgNode('title', {}, `${label}. ${detail}`));
        rect.addEventListener('mouseenter', () => { r02Detail.textContent = `${label}. ${detail}`; });
        rect.addEventListener('focus', () => { r02Detail.textContent = `${label}. ${detail}`; });
        r02Chart.append(rect);
      });
      const labelX = x + slot / 2;
      r02Chart.append(svgNode('text', {x: labelX, y: baseline + 20, transform: `rotate(-45 ${labelX} ${baseline + 20})`, 'text-anchor': 'end'}, row.ngay));
    });
    r02Chart.append(svgNode('text', {x: width / 2, y: 445, 'text-anchor': 'middle'}, 'Ngày có bản ghi (YYYY-MM-DD; không chèn ngày thiếu)'));
  }

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

  function query(id) {
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
    if (id === 'R01' && age !== '') {
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
    r02Chart.replaceChildren();
    r03Chart.replaceChildren();
    legend.replaceChildren();
    chartDetail.textContent = detailHint;
    error.hidden = true;
    panel.setAttribute('aria-busy', 'false');
  }

  function validate(data, params, id) {
    if (id === 'R03') {
      const doctors = new Set();
      const validRows = Array.isArray(data?.rows) && data.rows.every(row => {
        if (!row || !['ma_bac_si', 'ho_ten', 'chuyen_mon'].every(key => typeof row[key] === 'string') ||
            doctors.has(row.ma_bac_si) || !['so_lan_kham', 'so_dot', 'so_benh_nhan'].every(key => Number.isSafeInteger(row[key]) && row[key] >= 0)) return false;
        doctors.add(row.ma_bac_si);
        return true;
      });
      if (!data || data.report_id !== id || data.interval !== 'end_exclusive' || !validRows ||
          data.row_count !== data.rows.length || typeof data.data_notice !== 'string' ||
          data.filters?.start !== params.get('start') || data.filters?.end !== params.get('end') ||
          data.filters?.age_group !== undefined) throw new Error('Dữ liệu trả về không đúng hợp đồng R03. Chưa thể hiển thị kết quả.');
      return;
    }
    if (id === 'R02') {
      let previous = '';
      const validRows = Array.isArray(data?.rows) && data.rows.every(row => {
        if (!row || typeof row.ngay !== 'string' || row.ngay <= previous ||
            row.ngay < params.get('start') || row.ngay >= params.get('end')) return false;
        try { parseDate(row.ngay); } catch (_) { return false; }
        previous = row.ngay;
        return ['so_luot', 'so_lan_kham', 'so_benh_nhan_tiep_nhan'].every(key => Number.isSafeInteger(row[key]) && row[key] >= 0);
      });
      if (!data || data.report_id !== id || data.interval !== 'end_exclusive' || !validRows ||
          data.row_count !== data.rows.length || typeof data.data_notice !== 'string' ||
          data.filters?.start !== params.get('start') || data.filters?.end !== params.get('end') ||
          data.filters?.age_group !== undefined) throw new Error('Dữ liệu trả về không đúng hợp đồng R02. Chưa thể hiển thị kết quả.');
      return;
    }
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
    selectReport();
    status.textContent = `Bộ lọc đã đổi. Bấm Xem ${form.elements.report.value} để tải kết quả tương ứng.`;
  });
  form.addEventListener('submit', async event => {
    event.preventDefault();
    clear();
    const current = generation;
    let timer;
    let timedOut = false;
    try {
      const id = form.elements.report.value;
      if (!Object.hasOwn(reports, id)) throw new Error('Báo cáo chưa được hỗ trợ trong giao diện.');
      const spec = reports[id];
      const fields = spec.fields;
      const params = query(id);
      controller = new AbortController();
      const requestController = controller;
      timer = setTimeout(() => { timedOut = true; requestController.abort(); }, 20000);
      panel.setAttribute('aria-busy', 'true');
      status.textContent = `Đang tải ${id}…`;
      const endpoint = {R01: panel.dataset.endpoint, R02: panel.dataset.r02Endpoint, R03: panel.dataset.r03Endpoint}[id];
      const response = await fetch(`${endpoint}?${params}`, {signal: controller.signal, headers: {Accept: 'application/json'}});
      if (current !== generation) return;
      if (!response.ok) {
        const messages = {400: 'Bộ lọc bị API từ chối. Kiểm tra ngày và bộ lọc đã chọn.', 404: `Không tìm thấy API ${id}.`, 500: 'Máy chủ chưa xử lý được báo cáo.', 503: 'Chưa kết nối được MySQL. Kiểm tra kết nối rồi thử lại.'};
        throw new Error(`Lỗi ${response.status}: ${messages[response.status] || 'Không thể tải báo cáo.'}`);
      }
      const data = await response.json();
      if (current !== generation) return;
      validate(data, params, id);
      const head = panel.querySelector('#analytics-table thead tr');
      head.replaceChildren();
      spec.headers.forEach(label => {
        const cell = document.createElement('th'); cell.scope = 'col'; cell.textContent = label; head.append(cell);
      });
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
      const group = id === 'R01' ? (data.filters.age_group === undefined ? 'Tất cả nhóm' : `Nhóm ${data.filters.age_group}`) :
        id === 'R02' ? 'Lượt theo ngày vào; lần khám theo ngày khám' : 'Lần khám theo ngày khám; phân bố công việc, không xếp hạng chất lượng';
      const period = `${data.filters.start} ≤ ${id === 'R01' ? 'ngày khám' : 'ngày'} < ${data.filters.end}`;
      if (id === 'R01') renderChart(data, `${period}. ${group}`);
      else if (id === 'R02') renderR02(data, period);
      else renderR03(data, period);
      panel.querySelector('#analytics-applied').textContent = `Kỳ thực trả về: ${period}. ${group}. Số dòng: ${data.row_count} (không phải tổng bệnh nhân).`;
      panel.querySelector('#analytics-caption').textContent = `${id} — ${spec.title} · ${period} · ${group}`;
      panel.querySelector('.clinical-table').setAttribute('aria-label', `Bảng ${id}`);
      panel.querySelector('#analytics-table').dataset.report = id;
      panel.querySelector('#analytics-table-hint').textContent = id === 'R01' ?
        'Giữ thứ tự từ API. Mã nhóm -1 là ngày sinh không hợp lệ; 0/1/2/3 tương ứng 0–5/6–17/18–59/60+. Cuộn ngang để xem đủ cột.' : id === 'R02' ?
        'Giữ thứ tự ngày tăng từ API; chỉ những ngày được trả về. Lượt, người tiếp nhận trong ngày và lần khám là ba đơn vị riêng. Không cộng người theo ngày thành tổng người duy nhất. Cuộn ngang để xem đủ cột.' :
        'Giữ đủ bác sĩ và thứ tự API, gồm bác sĩ 0 hoạt động. Lần khám, đợt và bệnh nhân là ba đơn vị riêng; không cộng bệnh nhân giữa bác sĩ thành tổng người duy nhất. Không diễn giải thành chất lượng bác sĩ. Cuộn ngang để xem đủ cột.';
      panel.querySelector('#analytics-data-notice').textContent = data.data_notice;
      result.hidden = false;
      status.textContent = data.rows.length ? `Đã tải ${data.row_count} dòng ${id}.` : `Đã tải ${id}: không có dữ liệu phù hợp.`;
    } catch (exc) {
      if (current !== generation) return;
      result.hidden = true;
      body.replaceChildren();
      chart.replaceChildren();
      r02Chart.replaceChildren();
      r03Chart.replaceChildren();
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
  selectReport();
})();
