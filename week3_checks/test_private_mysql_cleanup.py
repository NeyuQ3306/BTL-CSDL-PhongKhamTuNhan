"""Private cleanup must not target a different executable, datadir or DB connection."""
import sys
from unittest.mock import Mock, MagicMock
import pytest
from tools import private_mysql_cleanup as cleanup


@pytest.mark.parametrize('args,expected', [
    (['mysqld', '--datadir=/private/data'], True),
    (['mysqld', '--datadir', '/private/data'], True),
    (['mysqld', '--datadir=/private/data-other'], False),
    (['mysqld', '--datadir=/system/data'], False),
    (['mysqld'], False)])
def test_exact_datadir_not_substring(args, expected):
    process = Mock()
    process.exe.return_value = sys.executable
    process.cmdline.return_value = args
    assert cleanup.matches_instance(process, sys.executable, '/private/data') is expected
    assert not cleanup.matches_instance(process, '/different/mysqld', '/private/data')


def database(datadir='/private/data', port=12345, failure=False):
    db = MagicMock()
    cursor = db.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = dict(datadir=datadir, port=port)
    if failure:
        cursor.execute.side_effect = RuntimeError('private failure text must not be logged')
    return db, cursor


def quiet(monkeypatch):
    monkeypatch.setattr(cleanup, 'instance_processes', lambda *_a: [])
    monkeypatch.setattr(cleanup, 'port_open', lambda _p: False)


def test_shutdown_then_close(monkeypatch):
    quiet(monkeypatch)
    db, cursor = database()
    result = cleanup.stop_private_mysql(None, db, sys.executable, '/private/data', 12345, timeout=.01)
    assert result['success'] and result['shutdown_requested']
    assert cursor.execute.call_args.args == ('SHUTDOWN',)
    db.close.assert_called_once()


@pytest.mark.parametrize('identity', [('other', 12345), ('/private/data', 3306)])
def test_wrong_connection_never_receives_shutdown(monkeypatch, identity):
    quiet(monkeypatch)
    db, cursor = database(*identity)
    result = cleanup.stop_private_mysql(None, db, sys.executable, '/private/data', 12345, timeout=.01)
    assert not result['shutdown_requested']
    assert all(call.args != ('SHUTDOWN',) for call in cursor.execute.call_args_list)
    assert result['errors'] == ['ValueError']


def test_connection_failure_still_closes_and_checks_processes(monkeypatch):
    quiet(monkeypatch)
    db, _ = database(failure=True)
    result = cleanup.stop_private_mysql(None, db, sys.executable, '/private/data', 12345, timeout=.01)
    assert result['success'] and result['errors'] == ['RuntimeError']
    assert 'private failure text' not in str(result)
    db.close.assert_called_once()
