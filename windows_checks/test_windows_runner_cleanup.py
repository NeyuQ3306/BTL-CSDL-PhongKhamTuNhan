"""Real Windows/MySQL startup, success exit and injected post-start failure."""
import json
import os
from pathlib import Path
import subprocess
import sys
import pytest


@pytest.mark.skipif(sys.platform != 'win32', reason='Windows process/runner integration')
@pytest.mark.parametrize('mode,exit_code', [('success', 0), ('error', 1)])
def test_private_mysql_runner_exit(mode, exit_code):
    mysqld = os.environ.get('W3_MYSQLD')
    if not mysqld:
        pytest.fail('W3_MYSQLD must point to isolated-test MySQL executable')
    root = Path(__file__).resolve().parents[1]
    before = set((root/'docs/evidence').glob('vuong_week2_prepare_*'))
    run = subprocess.run([sys.executable, '-m', 'tools.vuong_week2_prepare',
                          '--mysqld', mysqld, '--cleanup-check', mode],
                         cwd=root, capture_output=True, text=True, timeout=150)
    assert run.returncode == exit_code, run.stdout + run.stderr
    created = set((root/'docs/evidence').glob('vuong_week2_prepare_*')) - before
    assert len(created) == 1
    report = json.loads((created.pop()/'results.json').read_text(encoding='utf-8'))
    assert report['cleanup_check'] == mode
    assert report['mysql'].startswith('8.4.'), report['mysql']
    assert report['mysql_cleanup']['success']
    assert report['mysql_cleanup']['port_closed']
    assert report['mysql_cleanup']['remaining_pids'] == []
    assert report['mysql_cleanup']['launcher_exited']
    assert report['env_unchanged']
    assert report['preparation_success'] is False  # this smoke is not full UI acceptance
    if mode == 'error':
        assert report['failure_type'] == 'RuntimeError'
        assert report['mysql_cleanup']['fallback_pids']
        assert not report['mysql_cleanup']['shutdown_requested']
    else:
        assert report['mysql_cleanup']['shutdown_requested']
