"""Typed input at the service boundary; no float money or client supplied totals."""
import re
from datetime import date
from decimal import Decimal, InvalidOperation
from werkzeug.exceptions import UnprocessableEntity
from .validation import today_vn


def invalid(message):
    raise UnprocessableEntity(message)


def text(value, label, maximum=255):
    if not isinstance(value, str):
        invalid(f'{label}: phải là chuỗi.')
    value = value.strip()
    if not value or len(value) > maximum or any(ord(c) < 32 for c in value):
        invalid(f'{label}: bắt buộc, tối đa {maximum} ký tự, không có ký tự điều khiển.')
    return value


def code(value, label='Mã'):
    value = text(value, label, 12)
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,12}', value) or value.lower() == 'new':
        invalid(f'{label}: dùng chữ không dấu, số, gạch ngang/gạch dưới; không dùng new.')
    return value


def day(value, label='Ngày'):
    try:
        if not isinstance(value, str) or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', value):
            raise ValueError
        parsed = date.fromisoformat(value)
        if not date(1900, 1, 1) <= parsed <= today_vn():
            raise ValueError
        return parsed
    except ValueError:
        invalid(f'{label}: ngày hợp lệ từ 1900 đến hôm nay, dạng YYYY-MM-DD.')


def money(value):
    try:
        if not isinstance(value, str) or not re.fullmatch(r'[0-9]{1,12}(?:\.0{1,2})?', value):
            raise InvalidOperation
        amount = Decimal(value)
        if not amount.is_finite() or not 0 <= amount <= Decimal('999999999999'):
            raise InvalidOperation
        return amount
    except InvalidOperation:
        invalid('Tiền khám phải là số nguyên đồng không âm, tối đa 999999999999.')


def quantity(value):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{1,10}', value) or not 1 <= int(value) <= 2147483647:
        invalid('Số lượng thuốc phải là số nguyên dương, tối đa 2147483647.')
    return int(value)
