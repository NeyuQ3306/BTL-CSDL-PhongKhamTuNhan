"""One connection per Flask context; every write has explicit commit/rollback."""
from contextlib import contextmanager
import pymysql
from flask import current_app, g


def get_db():
    if 'db' not in g:
        cfg = current_app.config
        g.db = pymysql.connect(
            host=cfg['DB_HOST'], port=cfg['DB_PORT'], user=cfg['DB_USER'],
            password=cfg['DB_PASSWORD'], database=cfg['DB_NAME'],
            charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor,
            autocommit=False, connect_timeout=cfg['DB_CONNECT_TIMEOUT'],
            read_timeout=cfg['DB_READ_TIMEOUT'], write_timeout=10,
        )
        with g.db.cursor() as cur:
            cur.execute("SET time_zone = '+07:00'")
    return g.db


def close_db(_error=None):
    db = g.pop('db', None)
    if db is not None:
        try:
            db.rollback()  # also ends read transactions; never implicitly commits
        except pymysql.MySQLError:
            pass
        finally:
            db.close()


@contextmanager
def transaction():
    db = get_db()
    if g.get('in_transaction', False):
        raise RuntimeError('Nested transactions are not supported')
    g.in_transaction = True
    try:
        db.begin()
        yield db
        db.commit()
    except BaseException:
        db.rollback()
        raise
    finally:
        g.in_transaction = False


def fetch_all(sql, params=()):
    with get_db().cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def fetch_one(sql, params=()):
    with get_db().cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()
