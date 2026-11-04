/* R01–R06 presentation adapters. Counts and ordering come from the same API response. */
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
    R04: {title: 'Thuốc được kê', fields: ['ma_thuoc', 'ten_thuoc', 'don_vi_tinh', 'so_don', 'tong_so_luong'],
      headers: ['Mã thuốc', 'Tên thuốc', 'Đơn vị tính', 'Số đơn có thuốc (đơn)', 'Tổng lượng kê (theo đơn vị thuốc)']},
    R05: {title: 'Đợt tái mắc có tiền sử ghi nhận', fields: ['ma_dot', 'ma_benh_nhan', 'ho_ten', 'ma_benh', 'ten_benh', 'ngay_bat_dau', 'ngay_khoi_truoc', 'so_ngay_tu_lan_khoi_truoc'],
      headers: ['Mã đợt', 'Mã bệnh nhân', 'Họ tên', 'Mã bệnh', 'Tên bệnh', 'Ngày bắt đầu đợt mới', 'Ngày khỏi trước', 'Khoảng cách từ lần khỏi trước (ngày)']},
    R06: {title: 'Lâu chưa ghi nhận khám', fields: ['ma_dot', 'ma_benh_nhan', 'ho_ten', 'so_dien_thoai', 'ma_benh', 'ten_benh', 'ma_bac_si', 'ten_bac_si', 'ngay_bat_dau', 'ngay_kham_cuoi', 'chua_co_lan_kham', 'so_ngay_chua_ghi_nhan', 'nhom_ngay'],
      headers: ['Mã đợt', 'Mã bệnh nhân', 'Họ tên', 'Số điện thoại', 'Mã bệnh', 'Tên bệnh', 'Mã bác sĩ', 'Tên bác sĩ', 'Ngày bắt đầu', 'Ngày khám cuối', 'Chưa có lần khám (1=chưa khám, 0=đã có khám)', 'Số ngày chưa ghi nhận khám', 'Nhóm ngày']},
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
  const r04Chart = panel.querySelector('#r04-chart');
  const r05Chart = panel.querySelector('#r05-chart');
  const r06Chart = panel.querySelector('#r06-chart');
  const dayGroups = ['0–6', '7–13', '14–29', '30+'];

  function selectReport() {
    const id = form.elements.report.value;
    const isR01 = id === 'R01';
    const isR06 = id === 'R06';
    panel.querySelector('#analytics-age-field').hidden = !isR01;
    form.elements.age_group.disabled = !isR01;
    ['start', 'through'].forEach(name => {
      panel.querySelector(`#analytics-${name}-field`).hidden = isR06;
      form.elements[name].disabled = isR06;
    });
    ['as_of', 'threshold'].forEach(name => {
      const fieldId = name === 'as_of' ? 'as-of' : name;
      panel.querySelector(`#analytics-${fieldId}-field`).hidden = !isR06;
      form.elements[name].disabled = !isR06;
    });
    Object.keys(reports).forEach(report => {
      const prefix = report.toLowerCase();
      panel.querySelector(`#${prefix}-description`).hidden = report !== id;
      panel.querySelector(`#${prefix}-chart-section`).hidden = report !== id;
    });
    form.querySelector('button').textContent = `Xem ${id}`;
  }

  function renderHorizontal(data, period) {
    const id = data.report_id;
    const prefix = id.toLowerCase();
    const isDoctor = id === 'R03';
    const chartNode = panel.querySelector(`#${prefix}-chart`);
    const detailNode = panel.querySelector(`#${prefix}-chart-detail`);
    const metric = isDoctor ? 'so_lan_kham' : 'so_don';
    const codeKey = isDoctor ? 'ma_bac_si' : 'ma_thuoc';
    const nameKey = isDoctor ? 'ho_ten' : 'ten_thuoc';
    chartNode.replaceChildren();
    detailNode.textContent = 'Trỏ hoặc dùng Tab đến một thanh để xem chi tiết.';
    panel.querySelector(`#${prefix}-chart-period`).textContent = isDoctor ?
      `Kỳ thực trả về: ${period}. Số bác sĩ trả về: ${data.row_count}. Không loại bác sĩ có 0 hoạt động. Đơn vị thanh: lần khám; số đợt và bệnh nhân riêng trong bảng/chi tiết.` :
      `Kỳ thực trả về: ${period}. Số thuốc trả về: ${data.row_count}. Đơn vị thanh: đơn có thuốc; lượng kê và đơn vị riêng từng thuốc ở bảng/chi tiết.`;
    panel.querySelector(`#${prefix}-chart-empty`).hidden = data.rows.length !== 0;
    panel.querySelector(`#${prefix}-chart-scroll`).hidden = data.rows.length === 0;
    detailNode.hidden = data.rows.length === 0;
    if (!data.rows.length) return;
    const maximum = data.rows.reduce((n, row) => Math.max(n, row[metric]), 1);
    const step = Math.max(1, Math.ceil(maximum / 5));
    const axisMaximum = Math.ceil(maximum / step) * step;
    const width = 960, left = 250, plotWidth = 620, top = 50, rowHeight = 56;
    const bottom = top + data.rows.length * rowHeight;
    const height = bottom + 70;
    chartNode.setAttribute('viewBox', `0 0 ${width} ${height}`);
    chartNode.style.width = `${width}px`;
    chartNode.style.height = `${height}px`;
    chartNode.append(svgNode('title', {id: `${prefix}-svg-title`}, `${id} — ${reports[id].title}`));
    chartNode.append(svgNode('desc', {id: `${prefix}-svg-desc`}, isDoctor ?
      `${period}. Thanh ngang là số lần khám, giữ bác sĩ 0 hoạt động và thứ tự API. Không xếp hạng chất lượng. Tên đầy đủ, chuyên môn, số đợt và bệnh nhân có trong chi tiết và bảng.` :
      `${period}. Thanh ngang là số đơn có thuốc. Giữ lượng kê và đơn vị riêng từng thuốc trong bảng/chi tiết. Không gộp khác đơn vị hoặc suy ra lượng cần nhập.`));
    chartNode.append(svgNode('text', {x: 20, y: 24}, isDoctor ? 'Bác sĩ (mã / họ tên)' : 'Thuốc (mã / tên)'));
    for (let tick = 0; tick <= axisMaximum; tick += step) {
      const x = left + tick / axisMaximum * plotWidth;
      chartNode.append(svgNode('line', {x1: x, x2: x, y1: top - 10, y2: bottom, stroke: '#dbe3e8'}));
      chartNode.append(svgNode('text', {x, y: bottom + 24, 'text-anchor': 'middle'}, tick));
    }
    data.rows.forEach((row, index) => {
      const y = top + index * rowHeight;
      const detail = isDoctor ?
        `${row.ma_bac_si} — ${row.ho_ten}; chuyên môn: ${row.chuyen_mon}; ${row.so_lan_kham} lần khám, ${row.so_dot} đợt điều trị, ${row.so_benh_nhan} bệnh nhân khác nhau của bác sĩ trong kỳ. Không đánh giá chất lượng bác sĩ.` :
        `${row.ma_thuoc} — ${row.ten_thuoc}; ${row.so_don} đơn có thuốc; tổng lượng kê: ${row.tong_so_luong} ${row.don_vi_tinh}. Không phải lượng cần nhập.`;
      chartNode.append(svgNode('text', {x: left - 16, y: y + 10, 'text-anchor': 'end'}, row[codeKey]));
      const shortName = Array.from(row[nameKey]).slice(0, 27).join('');
      const label = svgNode('text', {x: left - 16, y: y + 30, 'text-anchor': 'end'}, shortName + (shortName === row[nameKey] ? '' : '…'));
      label.append(svgNode('title', {}, row[nameKey]));
      chartNode.append(label);
      const length = row[metric] / axisMaximum * plotWidth;
      const attributes = isDoctor ? {'data-doctor': row.ma_bac_si, 'data-examinations': row.so_lan_kham, 'data-episodes': row.so_dot, 'data-patients': row.so_benh_nhan} :
        {'data-drug': row.ma_thuoc, 'data-orders': row.so_don, 'data-quantity': row.tong_so_luong, 'data-unit': row.don_vi_tinh};
      const rect = svgNode('rect', {x: left, y, width: length, height: 34, fill: '#2563a6',
        class: 'chart-segment', tabindex: 0, role: 'img', 'aria-label': detail,
        ...attributes});
      rect.append(svgNode('title', {}, detail));
      rect.addEventListener('mouseenter', () => { detailNode.textContent = detail; });
      rect.addEventListener('focus', () => { detailNode.textContent = detail; });
      chartNode.append(rect);
      chartNode.append(svgNode('text', {x: left + length + 8, y: y + 23}, row[metric]));
    });
    chartNode.append(svgNode('text', {x: left + plotWidth / 2, y: height - 12, 'text-anchor': 'middle'}, isDoctor ? 'Số lần khám (lần)' : 'Số đơn có thuốc (đơn)'));
  }

  function renderGroupedEpisodes(data, period) {
    const isR06 = data.report_id === 'R06';
    const prefix = data.report_id.toLowerCase();
    const chartNode = panel.querySelector(`#${prefix}-chart`);
    const detailNode = panel.querySelector(`#${prefix}-chart-detail`);
    const groups = data.chart_groups;
    chartNode.replaceChildren();
    detailNode.textContent = 'Trỏ hoặc dùng Tab đến một cột để xem chi tiết.';
    panel.querySelector(`#${prefix}-chart-period`).textContent = isR06 ?
      `${period}. Số dòng hồ sơ sau lọc: ${data.row_count}. Đơn vị cột: đợt điều trị, không phải số bệnh nhân. Giữ đủ bốn nhóm, kể cả số 0.` :
      `Kỳ thực trả về: ${period}. Số dòng hồ sơ: ${data.row_count}. Biểu đồ theo nhóm API, đơn vị đợt tái mắc; không phải số bệnh nhân.`;
    panel.querySelector(`#${prefix}-chart-empty`).hidden = groups.length !== 0;
    panel.querySelector(`#${prefix}-chart-scroll`).hidden = groups.length === 0;
    detailNode.hidden = groups.length === 0;
    if (!groups.length) return;
    const maximum = groups.reduce((n, row) => Math.max(n, row.so_dot), 1);
    const step = Math.max(1, Math.ceil(maximum / 5));
    const axisMaximum = Math.ceil(maximum / step) * step;
    const width = Math.max(760, 110 + groups.length * 160);
    const left = 80, baseline = 328, plotHeight = 290;
    const slot = (width - left - 24) / groups.length;
    chartNode.setAttribute('viewBox', `0 0 ${width} 460`);
    chartNode.style.width = `${width}px`;
    chartNode.append(svgNode('title', {id: `${prefix}-svg-title`}, isR06 ? 'R06 — Số đợt theo nhóm ngày chưa ghi nhận khám' : 'R05 — Đợt tái mắc theo bệnh'));
    chartNode.append(svgNode('desc', {id: `${prefix}-svg-desc`}, isR06 ?
      `${period}. Cột lấy đủ bốn nhóm chart_groups sau lọc ngưỡng từ API, cùng response với bảng hồ sơ. Không chứa thông tin liên hệ, không kết luận trễ hẹn hoặc bỏ điều trị.` :
      `${period}. Cột lấy số đợt tái mắc từ chart_groups của API, cùng response với bảng hồ sơ. Không phải số bệnh nhân; thiếu lịch sử không có nghĩa chưa từng mắc.`));
    chartNode.append(svgNode('text', {x: left, y: 20}, isR06 ? 'Số đợt điều trị (đợt)' : 'Số đợt tái mắc (đợt)'));
    for (let tick = 0; tick <= axisMaximum; tick += step) {
      const y = baseline - tick / axisMaximum * plotHeight;
      chartNode.append(svgNode('line', {x1: left, x2: width - 24, y1: y, y2: y, stroke: '#dbe3e8'}));
      chartNode.append(svgNode('text', {x: left - 10, y: y + 4, 'text-anchor': 'end'}, tick));
    }
    groups.forEach((group, index) => {
      const x = left + index * slot + slot * 0.2;
      const height = group.so_dot / axisMaximum * plotHeight;
      const detail = isR06 ? `${group.nhom_ngay} ngày: ${group.so_dot} đợt điều trị sau lọc ngưỡng. Không phải số bệnh nhân; không kết luận trễ hẹn hoặc bỏ điều trị.` :
        `${group.ma_benh} — ${group.ten_benh}: ${group.so_dot} đợt tái mắc được ghi nhận, không phải số bệnh nhân. Thiếu lịch sử không có nghĩa chưa từng mắc.`;
      const attrs = isR06 ? {'data-group': group.nhom_ngay} : {'data-disease': group.ma_benh};
      const rect = svgNode('rect', {x, y: baseline - height, width: slot * 0.6, height, fill: '#2563a6',
        class: 'chart-segment', tabindex: 0, role: 'img', 'aria-label': detail,
        ...attrs, 'data-episodes': group.so_dot});
      rect.append(svgNode('title', {}, detail));
      rect.addEventListener('mouseenter', () => { detailNode.textContent = detail; });
      rect.addEventListener('focus', () => { detailNode.textContent = detail; });
      chartNode.append(rect);
      chartNode.append(svgNode('text', {x: x + slot * 0.3, y: baseline - height - 8, 'text-anchor': 'middle'}, group.so_dot));
      chartNode.append(svgNode('text', {x: x + slot * 0.3, y: baseline + 24, 'text-anchor': 'middle'}, isR06 ? group.nhom_ngay : group.ma_benh));
      if (!isR06) {
        const shortName = Array.from(group.ten_benh).slice(0, 19).join('');
        const label = svgNode('text', {x: x + slot * 0.3, y: baseline + 46, 'text-anchor': 'middle'}, shortName + (shortName === group.ten_benh ? '' : '…'));
        label.append(svgNode('title', {}, group.ten_benh));
        chartNode.append(label);
      }
    });
    chartNode.append(svgNode('text', {x: width / 2, y: 435, 'text-anchor': 'middle'}, isR06 ? 'Nhóm số ngày chưa ghi nhận khám (ngày)' : 'Bệnh (mã / tên; đầy đủ trong bảng và chi tiết)'));
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
    if (id === 'R06') {
      const asOf = form.elements.as_of.value;
      parseDate(asOf);
      const threshold = form.elements.threshold.value;
      if (!/^[0-9]{1,5}$/.test(threshold) || Number(threshold) > 36500) throw new Error('Ngưỡng phải là số nguyên từ 0 đến 36500.');
      return new URLSearchParams({as_of: asOf, threshold: String(Number(threshold))});
    }
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
    r04Chart.replaceChildren();
    r05Chart.replaceChildren();
    r06Chart.replaceChildren();
    legend.replaceChildren();
    chartDetail.textContent = detailHint;
    error.hidden = true;
    panel.setAttribute('aria-busy', 'false');
  }

  function validate(data, params, id) {
    if (id === 'R06') {
      const episodes = new Set();
      const labels = new Set();
      const validRows = Array.isArray(data?.rows) && data.rows.every(row => {
        if (!row || !['ma_dot', 'ma_benh_nhan', 'ho_ten', 'so_dien_thoai', 'ma_benh', 'ten_benh', 'ma_bac_si', 'ten_bac_si'].every(key => typeof row[key] === 'string') ||
            episodes.has(row.ma_dot) || ![0, 1].includes(row.chua_co_lan_kham) ||
            !Number.isSafeInteger(row.so_ngay_chua_ghi_nhan) || row.so_ngay_chua_ghi_nhan < 0 || !dayGroups.includes(row.nhom_ngay)) return false;
        try {
          parseDate(row.ngay_bat_dau);
          if (row.ngay_kham_cuoi !== null) parseDate(row.ngay_kham_cuoi);
        } catch (_) { return false; }
        if (row.ngay_bat_dau > params.get('as_of') || (row.ngay_kham_cuoi !== null && row.ngay_kham_cuoi > params.get('as_of')) ||
            (row.chua_co_lan_kham === 1) !== (row.ngay_kham_cuoi === null)) return false;
        episodes.add(row.ma_dot);
        return true;
      });
      const validGroups = Array.isArray(data?.chart_groups) && data.chart_groups.length === 4 && data.chart_groups.every(group => {
        if (!group || !dayGroups.includes(group.nhom_ngay) || labels.has(group.nhom_ngay) || !Number.isSafeInteger(group.so_dot) || group.so_dot < 0) return false;
        labels.add(group.nhom_ngay);
        return true;
      });
      if (!data || data.report_id !== id || data.interval !== 'end_of_as_of_day' || !validRows || !validGroups ||
          data.row_count !== data.rows.length || typeof data.data_notice !== 'string' ||
          data.filters?.as_of !== params.get('as_of') || data.filters?.threshold !== Number(params.get('threshold')) ||
          ['start', 'end', 'age_group'].some(key => data.filters?.[key] !== undefined)) {
        throw new Error('Dữ liệu trả về không đúng hợp đồng R06. Chưa thể hiển thị kết quả.');
      }
      return;
    }
    if (id === 'R05') {
      const episodes = new Set();
      const diseases = new Set();
      const validRows = Array.isArray(data?.rows) && data.rows.every(row => {
        if (!row || !['ma_dot', 'ma_benh_nhan', 'ho_ten', 'ma_benh', 'ten_benh'].every(key => typeof row[key] === 'string') ||
            episodes.has(row.ma_dot) || !Number.isSafeInteger(row.so_ngay_tu_lan_khoi_truoc) || row.so_ngay_tu_lan_khoi_truoc <= 0) return false;
        try { parseDate(row.ngay_bat_dau); parseDate(row.ngay_khoi_truoc); } catch (_) { return false; }
        if (row.ngay_bat_dau < params.get('start') || row.ngay_bat_dau >= params.get('end') || row.ngay_khoi_truoc >= row.ngay_bat_dau) return false;
        episodes.add(row.ma_dot);
        return true;
      });
      const validGroups = Array.isArray(data?.chart_groups) && data.chart_groups.every(group => {
        if (!group || typeof group.ma_benh !== 'string' || typeof group.ten_benh !== 'string' ||
            diseases.has(group.ma_benh) || !Number.isSafeInteger(group.so_dot) || group.so_dot < 0) return false;
        diseases.add(group.ma_benh);
        return true;
      });
      if (!data || data.report_id !== id || data.interval !== 'end_exclusive' || !validRows || !validGroups ||
          data.row_count !== data.rows.length || typeof data.data_notice !== 'string' ||
          data.filters?.start !== params.get('start') || data.filters?.end !== params.get('end') ||
          data.filters?.age_group !== undefined || (data.rows.length === 0) !== (data.chart_groups.length === 0)) {
        throw new Error('Dữ liệu trả về không đúng hợp đồng R05. Chưa thể hiển thị kết quả.');
      }
      return;
    }
    if (id === 'R04') {
      const drugs = new Set();
      const validRows = Array.isArray(data?.rows) && data.rows.every(row => {
        if (!row || !['ma_thuoc', 'ten_thuoc', 'don_vi_tinh'].every(key => typeof row[key] === 'string') ||
            drugs.has(row.ma_thuoc) || !['so_don', 'tong_so_luong'].every(key => Number.isSafeInteger(row[key]) && row[key] >= 0)) return false;
        drugs.add(row.ma_thuoc);
        return true;
      });
      if (!data || data.report_id !== id || data.interval !== 'end_exclusive' || !validRows ||
          data.row_count !== data.rows.length || typeof data.data_notice !== 'string' ||
          data.filters?.start !== params.get('start') || data.filters?.end !== params.get('end') ||
          data.filters?.age_group !== undefined) throw new Error('Dữ liệu trả về không đúng hợp đồng R04. Chưa thể hiển thị kết quả.');
      return;
    }
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
      const endpoint = {R01: panel.dataset.endpoint, R02: panel.dataset.r02Endpoint, R03: panel.dataset.r03Endpoint, R04: panel.dataset.r04Endpoint, R05: panel.dataset.r05Endpoint, R06: panel.dataset.r06Endpoint}[id];
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
          cell.textContent = id === 'R06' && key === 'ngay_kham_cuoi' && row[key] === null ? 'Chưa có lần khám' : String(row[key]);
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
        id === 'R02' ? 'Lượt theo ngày vào; lần khám theo ngày khám' : id === 'R03' ? 'Lần khám theo ngày khám; phân bố công việc, không xếp hạng chất lượng' : id === 'R04' ? 'Đơn theo ngày lập; lượng kê theo đơn vị riêng từng thuốc' : id === 'R05' ? 'Đợt tái mắc theo ngày bắt đầu; không phải số bệnh nhân' : 'Đợt đang điều trị tại ngày đối chiếu; không kết luận trễ hẹn hoặc bỏ điều trị';
      const period = id === 'R06' ? `Ngày đối chiếu: ${data.filters.as_of} (cuối ngày); ngưỡng ≥ ${data.filters.threshold} ngày` :
        `${data.filters.start} ≤ ${id === 'R01' ? 'ngày khám' : id === 'R05' ? 'ngày bắt đầu' : 'ngày'} < ${data.filters.end}`;
      if (id === 'R01') renderChart(data, `${period}. ${group}`);
      else if (id === 'R02') renderR02(data, period);
      else if (id === 'R05' || id === 'R06') renderGroupedEpisodes(data, period);
      else renderHorizontal(data, period);
      panel.querySelector('#analytics-applied').textContent = `Kỳ thực trả về: ${period}. ${group}. Số dòng: ${data.row_count} (${id === 'R04' ? 'số thuốc, không phải tổng đơn hoặc tổng lượng' : 'không phải tổng bệnh nhân'}).`;
      panel.querySelector('#analytics-caption').textContent = `${id} — ${spec.title} · ${period} · ${group}`;
      panel.querySelector('.clinical-table').setAttribute('aria-label', `Bảng ${id}`);
      panel.querySelector('#analytics-table').dataset.report = id;
      panel.querySelector('#analytics-table-hint').textContent = id === 'R01' ?
        'Giữ thứ tự từ API. Mã nhóm -1 là ngày sinh không hợp lệ; 0/1/2/3 tương ứng 0–5/6–17/18–59/60+. Cuộn ngang để xem đủ cột.' : id === 'R02' ?
        'Giữ thứ tự ngày tăng từ API; chỉ những ngày được trả về. Lượt, người tiếp nhận trong ngày và lần khám là ba đơn vị riêng. Không cộng người theo ngày thành tổng người duy nhất. Cuộn ngang để xem đủ cột.' : id === 'R03' ?
        'Giữ đủ bác sĩ và thứ tự API, gồm bác sĩ 0 hoạt động. Lần khám, đợt và bệnh nhân là ba đơn vị riêng; không cộng bệnh nhân giữa bác sĩ thành tổng người duy nhất. Không diễn giải thành chất lượng bác sĩ. Cuộn ngang để xem đủ cột.' : id === 'R04' ?
        'Giữ thứ tự API và lượng kê/đơn vị riêng từng thuốc. Số đơn có thuốc khác tổng lượng kê; không cộng lượng khác đơn vị hoặc suy ra lượng cần nhập. Cuộn ngang để xem đủ cột.' : id === 'R05' ?
        'Giữ đủ hồ sơ và thứ tự API: bệnh/ngày bắt đầu/mã đợt. Mỗi dòng là một đợt tái mắc, không phải một người duy nhất. Thiếu lịch sử không có nghĩa chưa từng mắc. Cuộn ngang để xem đủ cột.' :
        'Giữ thứ tự ưu tiên từ API: số ngày giảm, mã đợt tăng. NULL ngày khám cuối hiển thị “Chưa có lần khám”, không giả tạo ngày khám. Số điện thoại chỉ ở bảng dữ liệu giả lập. Không gọi trễ hẹn hoặc bỏ điều trị. Cuộn ngang để xem đủ 13 cột.';
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
      r04Chart.replaceChildren();
      r05Chart.replaceChildren();
      r06Chart.replaceChildren();
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
