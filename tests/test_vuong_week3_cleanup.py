"""Cleanup contracts: actual helper + final session, without any system DB."""
import json
import subprocess
from unittest.mock import Mock, MagicMock

import pytest

from tools import private_mysql_cleanup as mysql
from tools import vuong_week3_demo as demo


@pytest.mark.parametrize('fault', ['none', 'shutdown', 'close', 'wait'])
def test_cleanup_recovery_records_final_session(tmp_path, monkeypatch, fault):
    monkeypatch.setattr(demo, 'ROOT', tmp_path)
    monkeypatch.setattr(demo, 'port_open', lambda port: False)
    monkeypatch.setattr(mysql, 'port_open', lambda port: False)
    owned = Mock(pid=123)
    # A private child survives until scoped termination on failure paths.
    monkeypatch.setattr(mysql, 'instance_processes', Mock(side_effect=[
        [owned], []] if fault != 'none' else [[], [], []]))
    monkeypatch.setattr(mysql, 'matches_instance', lambda *args: True)
    monkeypatch.setattr(mysql.psutil, 'wait_procs', Mock(return_value=([], [])))
    monkeypatch.setattr(mysql.time, 'monotonic', Mock(side_effect=[0, 20]))
    db = MagicMock()
    cursor = db.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = dict(datadir=str(tmp_path/'data'), port=12345)
    if fault == 'shutdown':
        cursor.execute.side_effect = [None, RuntimeError('secret must not be recorded')]
    if fault == 'close':
        db.close.side_effect = RuntimeError('secret must not be recorded')
    proc = Mock()
    proc.poll.return_value = None if fault == 'wait' else 0
    if fault == 'wait':
        proc.wait.side_effect = subprocess.TimeoutExpired('mysqld', 10)
    log = (tmp_path/'mysql.log').open('wb')
    server, thread = Mock(server_port=12346), Mock()
    thread.is_alive.side_effect = [True, False]
    report = dict(success=True)
    demo.finish_session(tmp_path, report, proc=proc, db=db, server=server,
                        thread=thread, log=log, executable=tmp_path/'mysqld',
                        data=tmp_path/'data', port=12345, old_env=None,
                        manifest={}, protected={})
    final = json.loads((tmp_path/'session.json').read_text())
    proc.wait.assert_called_once()
    db.close.assert_called_once()
    server.server_close.assert_called_once()
    assert log.closed and final['log_closed'] and final['finished_at']
    assert final['success'] == (fault != 'wait')
    assert final['workload_success'] is True
    assert 'secret' not in (tmp_path/'session.json').read_text()
    if fault != 'none':
        owned.terminate.assert_called_once()
    if fault in ('shutdown', 'close'):
        assert 'RuntimeError' in final['mysql_cleanup']['errors']
    if fault == 'wait':
        assert not final['mysql_cleanup']['launcher_exited']
        assert final['mysql_cleanup']['remaining_pids'] == []


@pytest.mark.parametrize('stage', ['app_shutdown', 'app_close', 'app_join', 'mysql_cleanup', 'log_close', 'source_unchanged'])
def test_cleanup_stage_failure_does_not_skip_session(tmp_path, monkeypatch, stage):
    monkeypatch.setattr(demo, 'ROOT', tmp_path)
    monkeypatch.setattr(demo, 'port_open', lambda port: False)
    cleanup = Mock(return_value=dict(success=True))
    monkeypatch.setattr(demo, 'stop_private_mysql', cleanup)
    server, thread, log = Mock(server_port=42), Mock(), Mock(closed=True)
    thread.is_alive.side_effect = [True, False]
    actions = dict(app_shutdown=server.shutdown, app_close=server.server_close,
                   app_join=thread.join, mysql_cleanup=cleanup, log_close=log.close)
    if stage in actions:
        actions[stage].side_effect = OSError('private credential')
    report = dict(success=False, failure=dict(type='OriginalWorkloadError'))
    demo.finish_session(tmp_path, report, proc=None, db=None, server=server,
                        thread=thread, log=log, executable='unused', data='unused',
                        port=41, old_env=None,
                        manifest={'missing.py': 'hash'} if stage == 'source_unchanged' else {},
                        protected={})
    final = json.loads((tmp_path/'session.json').read_text())
    assert not final['success'] and not final['workload_success']
    assert final['failure']['type'] == 'OriginalWorkloadError'
    assert final['cleanup_errors'][0]['stage'] == stage
    assert final['finished_at'] and final['mysql_port_closed']
    cleanup.assert_called_once()
    log.close.assert_called_once()
    assert 'credential' not in (tmp_path/'session.json').read_text()


def test_identity_mismatch_never_sends_shutdown(monkeypatch, tmp_path):
    db = MagicMock()
    cursor = db.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = dict(datadir=str(tmp_path/'system'), port=3306)
    monkeypatch.setattr(mysql, 'instance_processes', lambda *args: [])
    monkeypatch.setattr(mysql, 'port_open', lambda port: False)
    monkeypatch.setattr(mysql.psutil, 'wait_procs', Mock(return_value=([], [])))
    result = mysql.stop_private_mysql(None, db, 'mysqld', tmp_path/'private', 12345)
    assert [call.args[0] for call in cursor.execute.call_args_list] == [
        'SELECT @@datadir AS datadir, @@port AS port']
    assert result['shutdown_requested'] is False and 'ValueError' in result['errors']
    db.close.assert_called_once()


@pytest.mark.parametrize('exe,args,expected', [
    ('private-mysqld', ['mysqld', '--datadir=private-data'], True),
    ('private-mysqld', ['mysqld', '--datadir', 'private-data'], True),
    ('system-mysqld', ['mysqld', '--datadir=private-data'], False),
    ('private-mysqld', ['mysqld', '--datadir=system-data'], False),
    ('private-mysqld', ['mysqld'], False),
])
def test_process_scope_requires_executable_and_exact_datadir(exe, args, expected):
    process = Mock()
    process.exe.return_value = exe
    process.cmdline.return_value = args
    assert mysql.matches_instance(process, 'private-mysqld', 'private-data') is expected
