"""Week-3 release checks against an explicit week-2 or final integrated snapshot."""
import os
from decimal import Decimal
from unittest.mock import Mock

import pymysql
import pytest
from flask import g
from werkzeug.exceptions import HTTPException
from clinic_app import create_app
from clinic_app import db as database


@pytest.fixture
def unit_app():
    return create_app({'TESTING': True, 'SECRET_KEY': 'week3-disposable-session'})


@pytest.mark.parametrize('value', ['0', '0.00', '999999999999', '999999999999.00'])
def test_money_boundary_exact_decimal(value):
    from clinic_app.workflow_validation import money
    result = money(value)
    assert isinstance(result, Decimal)
    assert result == Decimal(value)


@pytest.mark.parametrize('value', [None, '', 'NaN', 'Infinity', '-0', '1.01', '1000000000000', '1,000', '1e3'])
def test_money_invalid_rejected(value):
    from clinic_app.workflow_validation import money
    with pytest.raises(HTTPException) as exc:
        money(value)
    assert exc.value.code == 422


@pytest.mark.parametrize('phase', ['body', 'commit'])
def test_transaction_failure_rolls_back_and_next_transaction_works(unit_app, monkeypatch, phase):
    connection = Mock()
    monkeypatch.setattr(database, 'get_db', lambda: connection)
    failure = pymysql.OperationalError(1213, 'simulated transaction failure')
    if phase == 'commit':
        connection.commit.side_effect = [failure, None]
    with unit_app.app_context():
        with pytest.raises(pymysql.OperationalError):
            with database.transaction():
                if phase == 'body':
                    raise failure
        assert connection.rollback.call_count == 1
        assert not g.in_transaction
        with database.transaction():
            pass
        assert connection.begin.call_count == 2
        assert connection.commit.call_count == (2 if phase == 'commit' else 1)


def test_teardown_never_commits_and_closes_after_rollback_failure(unit_app):
    connection = Mock()
    connection.rollback.side_effect = pymysql.OperationalError(2006, 'simulated disconnect')
    with unit_app.app_context():
        g.db = connection
    connection.commit.assert_not_called()
    connection.close.assert_called_once()


@pytest.fixture
def live_app():
    if os.getenv('RUN_MYSQL_TESTS') != '1':
        pytest.skip('Real MySQL checks require RUN_MYSQL_TESTS=1')
    if not os.getenv('DB_NAME', '').endswith('_test'):
        pytest.fail('Use an isolated database ending in _test')
    return create_app({'TESTING': True, 'SECRET_KEY': 'week3-live-session'})


@pytest.fixture
def patient(live_app):
    from clinic_app.db import transaction
    with live_app.app_context():
        with transaction() as db, db.cursor() as cur:
            cur.execute('INSERT INTO benh_nhan VALUES (%s,%s,%s,%s,%s,%s)',
                        ('W3P1', '999000003001', 'Week3 fictional patient', '1980-01-01', 'Test', '0900000001'))
    try:
        yield 'W3P1'
    finally:
        with live_app.app_context():
            with transaction() as db, db.cursor() as cur:
                cur.execute("DELETE c FROM chi_tiet_don_thuoc c JOIN don_thuoc p ON p.ma_don=c.ma_don JOIN lan_kham_benh k ON k.ma_lan_kham=p.ma_lan_kham JOIN dot_dieu_tri d ON d.ma_dot=k.ma_dot WHERE d.ma_benh_nhan='W3P1'")
                cur.execute("DELETE p FROM don_thuoc p JOIN lan_kham_benh k ON k.ma_lan_kham=p.ma_lan_kham JOIN dot_dieu_tri d ON d.ma_dot=k.ma_dot WHERE d.ma_benh_nhan='W3P1'")
                cur.execute("DELETE k FROM lan_kham_benh k JOIN dot_dieu_tri d ON d.ma_dot=k.ma_dot WHERE d.ma_benh_nhan='W3P1'")
                cur.execute("DELETE h FROM ho_tro h JOIN luot_den_kham l ON l.ma_luot=h.ma_luot WHERE l.ma_benh_nhan='W3P1'")
                for table in ('luot_den_kham', 'dot_dieu_tri', 'benh_nhan'):
                    cur.execute(f'DELETE FROM {table} WHERE ma_benh_nhan=%s', ('W3P1',))


def visit(cost='0'):
    return dict(ma_luot='W3L1', ma_benh_nhan='W3P1', ngay_vao_vien='2002-01-01',
                che_do_dot='new', ma_dot='W3D1', ma_benh='B001', ma_bac_si='BS001',
                ma_lan_kham='W3K1', ngay_kham='2002-01-01', tien_kham_chua=cost,
                ket_luan='Week3 check', ma_y_ta='YT001', ngay_ho_tro='2002-01-01', noi_dung_ho_tro='Test')


def test_empty_history_then_open_dates_are_null(live_app, patient):
    from clinic_app import reports, workflows
    with live_app.app_context():
        empty = reports.history(patient)
        assert all(empty[key] == [] for key in ('visits', 'treatments', 'current', 'examinations', 'medicines', 'support'))
        workflows.create_visit(visit())
    client = live_app.test_client()
    response = client.get('/reports/history?patient_id=W3P1&format=json')
    assert response.status_code == 200
    assert response.json['visits'][0]['ngay_ra_vien'] is None
    assert response.json['treatments'][0]['ngay_khoi'] is None
    assert Decimal(response.json['examinations'][0]['tien_kham_chua']) == 0
    assert response.json['examinations'][0]['ma_don'] is None
    assert client.get('/patients/W3P1/history').status_code == 200


def test_maximum_money_persists_exactly(live_app, patient):
    from clinic_app import workflows
    from clinic_app.db import fetch_one
    with live_app.app_context():
        workflows.create_visit(visit('999999999999'))
        assert fetch_one('SELECT tien_kham_chua FROM lan_kham_benh WHERE ma_lan_kham=%s', ('W3K1',))['tien_kham_chua'] == Decimal('999999999999')
    result = live_app.test_client().get('/reports/history?patient_id=W3P1&format=json')
    assert result.status_code == 200
    assert result.json['examinations'][0]['tien_kham_chua'] == '999999999999'


def test_invalid_money_leaves_no_partial_visit(live_app, patient):
    from clinic_app import workflows
    from clinic_app.db import fetch_one
    with live_app.app_context():
        with pytest.raises(HTTPException) as exc:
            workflows.create_visit(visit('1000000000000'))
        assert exc.value.code == 422
        for table, key, value in [('luot_den_kham','ma_luot','W3L1'), ('dot_dieu_tri','ma_dot','W3D1'), ('lan_kham_benh','ma_lan_kham','W3K1')]:
            assert fetch_one(f'SELECT COUNT(*) n FROM {table} WHERE {key}=%s', (value,))['n'] == 0


def test_second_drug_failure_allows_retry_same_order_id(live_app, patient):
    from clinic_app import workflows
    from clinic_app.db import fetch_one
    data = dict(ma_don='W3RX1', ngay_lap_don='2002-01-01')
    good = dict(ma_thuoc='T001', so_luong='2', lieu_dung='Test')
    bad = dict(ma_thuoc='ZZW3MISSING', so_luong='1', lieu_dung='Test')
    with live_app.app_context():
        workflows.create_visit(visit())
        with pytest.raises(HTTPException) as exc:
            workflows.prescribe('W3K1', data, [good, bad])
        assert exc.value.code == 404
        for table in ('don_thuoc', 'chi_tiet_don_thuoc'):
            assert fetch_one(f'SELECT COUNT(*) n FROM {table} WHERE ma_don=%s', ('W3RX1',))['n'] == 0
        assert workflows.prescribe('W3K1', data, [good]) == 'W3RX1'
        assert fetch_one('SELECT COUNT(*) n FROM chi_tiet_don_thuoc WHERE ma_don=%s', ('W3RX1',))['n'] == 1


@pytest.mark.parametrize('path', ['/visits/W3MISSING', '/prescriptions/W3MISSING', '/patients/W3MISSING/history', '/reports/history?patient_id=W3MISSING&format=json'])
def test_missing_data_returns_404(live_app, path):
    response = live_app.test_client().get(path)
    assert response.status_code == 404
    if 'format=json' in path:
        assert response.is_json and set(response.json) == {'error'}
