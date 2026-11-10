"""Normalize SQL identifiers only; never rewrite quoted demo values."""
import argparse
import hashlib
import re
from pathlib import Path

TOKEN = re.compile(r"'(?:''|\\.|[^'\\])*'|--[^\n]*|/\*[\s\S]*?\*/|`[^`]+`|[A-Za-z_][A-Za-z_0-9]*")
TABLES = {'BAC_SI', 'Y_TA', 'BENH_NHAN', 'BENH', 'THUOC', 'DOT_DIEU_TRI',
          'LUOT_DEN_KHAM', 'LAN_KHAM_BENH', 'DON_THUOC', 'CHI_TIET_DON_THUOC', 'HO_TRO'}
COLUMNS = ('MaBacSi CMT HoTen NgaySinh DiaChi BacNghe ThamNien ChuyenMon TrinhDoDaoTao '
           'MaYTa SoDienThoai TrinhDo MaBenhNhan MaBenh TenBenh MaThuoc TenThuoc DonViTinh '
           'GiaHienTai MaDot NgayBatDau NgayKhoi TrangThai MaLuot NgayVaoVien NgayRaVien '
           'MaLanKham SoThuTuTrongDot NgayKham TienKhamChua KetLuan MaDon NgayLapDon '
           'SoLuong LieuDung DonGiaBan NoiDungHoTro NgayHoTro').split()
MAPPING = {x: re.sub(r'(?<!^)(?=[A-Z][a-z])', '_', x).lower() for x in COLUMNS}
MAPPING['CMT'] = 'cccd'
MAPPING['cmt'] = 'cccd'
MAPPING['CCCD'] = 'cccd'
MAPPING['MaYTa'] = 'ma_y_ta'
MAPPING.update({x: x.lower() for x in TABLES})

def normalize(source):
    def replace(match):
        token = match.group()
        if token.startswith('`'):
            return '`' + MAPPING.get(token[1:-1], token[1:-1]) + '`'
        return MAPPING.get(token, token)
    source = re.sub(r'^CREATE DATABASE[^\n]*\n|^USE [^\n]*\n', '', source, flags=re.M)
    return TOKEN.sub(replace, source)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    raw = args.source.read_bytes()
    result = normalize(raw.decode('utf-8-sig'))
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    args.destination.write_text('-- Adapter tuần 1 của Trung; dữ liệu giả lập do Vũ Đại Vương bàn giao.\n'
                                '-- SHA256 nguồn: ' + hashlib.sha256(raw).hexdigest() + '\n'
                                '-- Chỉ đổi tên bảng/cột, bỏ CREATE DATABASE/USE; không đổi giá trị dữ liệu.\n'
                                + result, encoding='utf-8')
    print(args.destination)
