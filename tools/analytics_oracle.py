"""Independent Python oracle: raw rows -> expected report rows, no report SQL."""
import ast
import json
import re
from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


def seed_rows():
    text = (Path(__file__).resolve().parents[1] / 'database/seed.sql').read_text(encoding='utf-8')
    result = {}
    for match in re.finditer(r'INSERT INTO (\w+) \(([^)]+)\) VALUES\s*(.*?);', text, re.S):
        columns = [x.strip() for x in match[2].split(',')]
        values = ast.literal_eval('[' + re.sub(r'\bNULL\b', 'None', match[3]) + ']')
        result[match[1]] = [dict(zip(columns, row)) for row in values]
    return result


def normalize(value):
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalize(x) for x in value]
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral() else str(value.normalize())
    return value


def canonical(rows):
    return sorted(json.dumps(normalize(row), sort_keys=True, ensure_ascii=False) for row in rows)


def expected(raw, start, end, as_of, threshold=14):
    data = normalize(raw)
    episodes = {x['ma_dot']: x for x in data['dot_dieu_tri']}
    patients = {x['ma_benh_nhan']: x for x in data['benh_nhan']}
    diseases = {x['ma_benh']: x['ten_benh'] for x in data['benh']}
    doctors = {x['ma_bac_si']: x for x in data['bac_si']}
    drugs = {x['ma_thuoc']: x for x in data['thuoc']}
    exams = defaultdict(list)
    orders = {x['ma_lan_kham']: x for x in data['don_thuoc']}
    details = defaultdict(list)
    for x in data['chi_tiet_don_thuoc']:
        details[x['ma_don']].append(x)
    for x in data['lan_kham_benh']:
        exams[x['ma_dot']].append(x)
    output = {f'R{i:02}': [] for i in range(1, 8)}
    age_groups = defaultdict(lambda: [set(), set()])
    for eid, history in exams.items():
        days = [x['ngay_kham'] for x in history if start <= x['ngay_kham'] < end]
        if not days:
            continue
        episode = episodes[eid]
        birth = date.fromisoformat(patients[episode['ma_benh_nhan']]['ngay_sinh'])
        day = date.fromisoformat(min(days))
        age = day.year - birth.year - ((day.month, day.day) < (birth.month, birth.day))
        group = -1 if birth > day else 0 if age < 6 else 1 if age < 18 else 2 if age < 60 else 3
        ids, people = age_groups[(episode['ma_benh'], group)]
        ids.add(eid)
        people.add(episode['ma_benh_nhan'])
    for (disease, group), (ids, people) in age_groups.items():
        output['R01'].append(dict(ma_benh=disease, ten_benh=diseases[disease], thu_tu_nhom=group,
            nhom_tuoi={-1:'Ngày sinh không hợp lệ',0:'0–5',1:'6–17',2:'18–59',3:'60+'}[group],
            so_dot=len(ids), so_benh_nhan=len(people)))
    days = defaultdict(lambda: [0, set(), 0])
    for x in data['luot_den_kham']:
        if start <= x['ngay_vao_vien'] < end:
            values = days[x['ngay_vao_vien']]
            values[0] += 1
            values[1].add(x['ma_benh_nhan'])
    for x in data['lan_kham_benh']:
        if start <= x['ngay_kham'] < end:
            days[x['ngay_kham']][2] += 1
    for day, (visits, people, count) in days.items():
        output['R02'].append(dict(ngay=day, so_luot=visits, so_benh_nhan_tiep_nhan=len(people), so_lan_kham=count))
    for did, doctor in doctors.items():
        selected = [x for x in data['lan_kham_benh'] if start <= x['ngay_kham'] < end
                    and episodes[x['ma_dot']]['ma_bac_si'] == did]
        output['R03'].append(dict(ma_bac_si=did, ho_ten=doctor['ho_ten'], chuyen_mon=doctor['chuyen_mon'],
            so_lan_kham=len(selected), so_dot=len({x['ma_dot'] for x in selected}),
            so_benh_nhan=len({episodes[x['ma_dot']]['ma_benh_nhan'] for x in selected})))
    medicine = defaultdict(lambda: [set(), 0])
    for order in data['don_thuoc']:
        if start <= order['ngay_lap_don'] < end:
            for item in details[order['ma_don']]:
                values = medicine[item['ma_thuoc']]
                values[0].add(order['ma_don'])
                values[1] += item['so_luong']
    for mid, (ids, quantity) in medicine.items():
        drug = drugs[mid]
        output['R04'].append(dict(ma_thuoc=mid, ten_thuoc=drug['ten_thuoc'], don_vi_tinh=drug['don_vi_tinh'],
                                 so_don=len(ids), tong_so_luong=quantity))
    for eid, episode in episodes.items():
        person = patients[episode['ma_benh_nhan']]
        disease = episode['ma_benh']
        if start <= episode['ngay_bat_dau'] < end:
            prior = [x['ngay_khoi'] for x in episodes.values() if x['ma_benh_nhan'] == episode['ma_benh_nhan']
                     and x['ma_benh'] == disease and x['ngay_khoi'] and x['ngay_khoi'] < episode['ngay_bat_dau']]
            if prior:
                last = max(prior)
                output['R05'].append(dict(ma_dot=eid, ma_benh_nhan=episode['ma_benh_nhan'],ho_ten=person['ho_ten'],
                    ma_benh=disease,ten_benh=diseases[disease],ngay_bat_dau=episode['ngay_bat_dau'],
                    ngay_khoi_truoc=last,so_ngay_tu_lan_khoi_truoc=(date.fromisoformat(episode['ngay_bat_dau'])-date.fromisoformat(last)).days))
        if episode['ngay_bat_dau'] <= as_of and (not episode['ngay_khoi'] or episode['ngay_khoi'] > as_of):
            history = [x['ngay_kham'] for x in exams[eid] if x['ngay_kham'] <= as_of]
            last = max(history) if history else None
            gap = (date.fromisoformat(as_of)-date.fromisoformat(last or episode['ngay_bat_dau'])).days
            if gap >= threshold:
                output['R06'].append(dict(ma_dot=eid,ma_benh_nhan=episode['ma_benh_nhan'],ho_ten=person['ho_ten'],
                    so_dien_thoai=person['so_dien_thoai'],ma_benh=disease,ten_benh=diseases[disease],
                    ma_bac_si=episode['ma_bac_si'],ten_bac_si=doctors[episode['ma_bac_si']]['ho_ten'],
                    ngay_bat_dau=episode['ngay_bat_dau'],ngay_kham_cuoi=last,chua_co_lan_kham=int(last is None),
                    so_ngay_chua_ghi_nhan=gap,nhom_ngay='0–6' if gap<7 else '7–13' if gap<14 else '14–29' if gap<30 else '30+'))
    costs = defaultdict(lambda: [[], 0])
    for eid, episode in episodes.items():
        if not episode['ngay_khoi'] or not start <= episode['ngay_khoi'] < end or episode['trang_thai'] != 'Đã khỏi':
            continue
        valid, excluded = costs[episode['ma_benh']]
        history = exams[eid]
        sequences = sorted(x['so_thu_tu_trong_dot'] for x in history)
        prescriptions = [orders[x['ma_lan_kham']] for x in history if x['ma_lan_kham'] in orders]
        if not history or sequences != list(range(1,len(history)+1)) or any(not details[x['ma_don']] for x in prescriptions):
            costs[episode['ma_benh']][1] += 1
            continue
        fees = sum(Decimal(x['tien_kham_chua']) for x in history)
        meds = sum((Decimal(x['so_luong'])*Decimal(x['don_gia_ban']) for p in prescriptions for x in details[p['ma_don']]), Decimal(0))
        valid.append((fees,meds))
    for disease, (valid, excluded) in costs.items():
        def avg(values):
            return (sum(values)/Decimal(len(valid))).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP) if valid else None
        totals = [a+b for a,b in valid]
        output['R07'].append(dict(ma_benh=disease,ten_benh=diseases[disease],so_dot_tinh=len(valid),so_dot_loai=excluded,
            tb_tien_kham=avg([a for a,b in valid]),tb_tien_thuoc=avg([b for a,b in valid]),tb_tong=avg(totals),
            min_tong=min(totals) if valid else None,max_tong=max(totals) if valid else None))
    return output
