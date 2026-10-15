"""Server validation, independent of HTML input constraints."""
import re
from datetime import date, datetime
from zoneinfo import ZoneInfo


def today_vn():
    return datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).date()


def validate(entity, form, fixed_id=None):
    values, errors = {}, {}
    for field in entity.fields:
        raw = form.get(field.name, '')
        value = raw.strip() if isinstance(raw, str) else ''
        values[field.name] = value
        if not value:
            errors[field.name] = 'Vui lòng nhập ' + field.label.lower() + '.'
            continue
        if field.kind not in ('date', 'integer') and len(value) > field.max_length:
            errors[field.name] = f'Tối đa {field.max_length} ký tự.'
            continue
        if field.kind == 'code' and not re.fullmatch(r'[A-Za-z0-9_-]{1,12}', value):
            errors[field.name] = 'Mã chỉ gồm chữ không dấu, số, gạch ngang hoặc gạch dưới.'
        elif field.kind == 'cmt' and not re.fullmatch(r'[0-9]{9,20}', value):
            errors[field.name] = 'CMT/CCCD phải có từ 9 đến 20 chữ số.'
        elif field.kind == 'phone' and not re.fullmatch(r'\+?[0-9]{9,15}', value):
            errors[field.name] = 'Số điện thoại gồm 9–15 chữ số, có thể bắt đầu bằng +.'
        elif field.kind == 'date':
            try:
                if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                    raise ValueError
                parsed = date.fromisoformat(value)
                if parsed > today_vn() or parsed < date(1900, 1, 1):
                    raise ValueError
                values[field.name] = parsed
            except ValueError:
                errors[field.name] = 'Ngày sinh hợp lệ từ 1900 đến hôm nay, dạng YYYY-MM-DD.'
        elif field.kind == 'integer':
            if not re.fullmatch(r'[0-9]{1,3}', value) or int(value) > 100:
                errors[field.name] = 'Thâm niên phải là số nguyên từ 0 đến 100.'
            else:
                values[field.name] = int(value)
        elif any(ord(c) < 32 for c in value):
            errors[field.name] = 'Không nhập ký tự điều khiển.'
    if fixed_id is not None and values[entity.pk] != fixed_id:
        errors[entity.pk] = 'Không được thay đổi mã hồ sơ khi sửa.'
    return values, errors
