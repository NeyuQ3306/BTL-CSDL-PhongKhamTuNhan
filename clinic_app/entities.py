"""Allowlisted identifiers and shared field contract for backend/Jinja."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Field:
    name: str
    label: str
    kind: str = 'text'
    max_length: int = 100


@dataclass(frozen=True)
class Entity:
    slug: str
    table: str
    pk: str
    title: str
    fields: tuple


COMMON = (Field('cccd', 'CCCD', 'cccd', 20), Field('ho_ten', 'Họ tên'),
          Field('ngay_sinh', 'Ngày sinh', 'date'), Field('dia_chi', 'Địa chỉ', 'text', 255))
PHONE = Field('so_dien_thoai', 'Số điện thoại', 'phone', 20)
YEARS = Field('tham_nien', 'Thâm niên (năm)', 'integer')
ENTITIES = {
    'patients': Entity('patients', 'benh_nhan', 'ma_benh_nhan', 'Bệnh nhân',
                       (Field('ma_benh_nhan', 'Mã bệnh nhân', 'code', 12), *COMMON, PHONE)),
    'doctors': Entity('doctors', 'bac_si', 'ma_bac_si', 'Bác sĩ',
                     (Field('ma_bac_si', 'Mã bác sĩ', 'code', 12), *COMMON,
                      Field('bac_nghe', 'Bậc nghề', 'text', 40), YEARS,
                      Field('chuyen_mon', 'Chuyên môn'), Field('trinh_do_dao_tao', 'Trình độ đào tạo'))),
    'nurses': Entity('nurses', 'y_ta', 'ma_y_ta', 'Y tá',
                    (Field('ma_y_ta', 'Mã y tá', 'code', 12), *COMMON, PHONE,
                     Field('trinh_do', 'Trình độ'), YEARS)),
}
