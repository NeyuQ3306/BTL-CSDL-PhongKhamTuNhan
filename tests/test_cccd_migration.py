"""Column rename compatibility, data preservation and resumable MySQL migration."""
import os
from pathlib import Path
from uuid import uuid4

import pymysql
import pytest

from clinic_app.entities import ENTITIES
from clinic_app.validation import validate
from tools.normalize_vuong import normalize
from tools.quyen_db import connect, statements

ROOT = Path(__file__).resolve().parents[1]
TABLES = ('bac_si', 'y_ta', 'benh_nhan')


def test_cccd_contract_and_legacy_sql_adapter():
    for entity in ENTITIES.values():
        fields = {f.name: f for f in entity.fields}
        assert 'cccd' in fields and 'cmt' not in fields
        assert fields['cccd'].kind == 'cccd'
    assert normalize("SELECT CMT, `CMT`, cmt, CCCD, 'CMT';") == "SELECT cccd, `cccd`, cccd, cccd, 'CMT';"
    e = ENTITIES['patients']
    data = dict(ma_benh_nhan='CCCD01', cccd='000123456789', ho_ten='Test',
                ngay_sinh='2000-01-01', dia_chi='Test', so_dien_thoai='0901234567')
    values, errors = validate(e, data)
    assert not errors and values['cccd'] == '000123456789'
    data['cccd'] = 'abc'
    assert 'cccd' in validate(e, data)[1]


@pytest.fixture
def migration_db():
    if os.getenv('RUN_MYSQL_TESTS') != '1':
        pytest.skip('Set RUN_MYSQL_TESTS=1 for disposable MySQL migration tests')
    if not os.getenv('DB_NAME', '').endswith('_test'):
        pytest.fail('DB_NAME must end with _test')
    db = connect()
    name = 'cccd_migration_' + uuid4().hex[:12] + '_test'
    try:
        with db.cursor() as c:
            c.execute(f'CREATE DATABASE `{name}` CHARACTER SET utf8mb4')
            c.execute(f'USE `{name}`')
            for table in TABLES:
                c.execute(f'CREATE TABLE `{table}` (id INT PRIMARY KEY, cmt VARCHAR(20) NOT NULL UNIQUE)')
                c.execute(f"INSERT INTO `{table}` VALUES (1, '000123456789')")
        db.commit()
        yield db
    finally:
        with db.cursor() as c:
            c.execute(f'DROP DATABASE IF EXISTS `{name}`')
        db.close()


def migrate(db):
    with db.cursor() as c:
        for sql in statements((ROOT / 'database/migrations/001_cmt_to_cccd.sql').read_text()):
            c.execute(sql)


def column_exists(db, table, name):
    with db.cursor() as c:
        c.execute('SELECT COUNT(*) AS n FROM information_schema.COLUMNS '
                  'WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND COLUMN_NAME=%s', (table, name))
        return bool(c.fetchone()['n'])


@pytest.mark.parametrize('mixed', [False, True])
def test_migration_preserves_values_constraints_and_can_rerun(migration_db, mixed):
    db = migration_db
    if mixed:
        with db.cursor() as c:
            c.execute('ALTER TABLE bac_si RENAME COLUMN cmt TO cccd')
    migrate(db)
    migrate(db)
    for table in TABLES:
        assert column_exists(db, table, 'cccd') and not column_exists(db, table, 'cmt')
        with db.cursor() as c:
            c.execute(f'SELECT cccd FROM `{table}` WHERE id=1')
            assert c.fetchone()['cccd'] == '000123456789'
            with pytest.raises(pymysql.IntegrityError):
                c.execute(f"INSERT INTO `{table}` VALUES (2, '000123456789')")
            with pytest.raises(pymysql.IntegrityError):
                c.execute(f'INSERT INTO `{table}` VALUES (3, NULL)')
            c.execute(f'SHOW INDEX FROM `{table}` WHERE Key_name=%s', ('cccd',))
            assert c.fetchone()['Non_unique'] == 0


@pytest.mark.parametrize('bad_state', ['both', 'neither', 'missing_table'])
def test_migration_preflight_rejects_invalid_state_before_any_rename(migration_db, bad_state):
    db = migration_db
    with db.cursor() as c:
        if bad_state == 'both':
            c.execute('ALTER TABLE benh_nhan ADD COLUMN cccd VARCHAR(20)')
        elif bad_state == 'neither':
            c.execute('ALTER TABLE benh_nhan RENAME COLUMN cmt TO legacy_identifier')
        else:
            c.execute('DROP TABLE benh_nhan')
    with pytest.raises(pymysql.MySQLError, match='Expected exactly one'):
        migrate(db)
    assert column_exists(db, 'bac_si', 'cmt')
    assert column_exists(db, 'y_ta', 'cmt')
