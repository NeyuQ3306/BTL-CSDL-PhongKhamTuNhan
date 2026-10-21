"""A release receipt must reject an incorrect source or dirty seed state."""
import json
from types import SimpleNamespace
from flask import Flask
import pytest
from tools import trung_week3_preflight as preflight


@pytest.fixture
def receipt_environment(monkeypatch):
    app = Flask('receipt-test')
    app.config['DB_NAME'] = 'receipt_test'
    state = dict(matches_expected_counts=True, findings={'check': []}, total=1144)
    controls = {'triggers': 9, 'sql_count': 10, 'sql_rows': []}
    monkeypatch.setattr(preflight, 'create_app', lambda: app)
    monkeypatch.setattr(preflight, 'audit', lambda: dict(state))
    monkeypatch.setattr(preflight, 'fetch_one', lambda *_args: {'n': controls['triggers']})
    monkeypatch.setattr(preflight, 'fetch_all', lambda *_args: controls['sql_rows'])
    monkeypatch.setattr(preflight, 'statements', lambda _text: ['SELECT 1'] * controls['sql_count'])
    monkeypatch.setattr(preflight.subprocess, 'run', lambda *a, **kw: SimpleNamespace(returncode=0, stdout='a'*40))
    return state, controls


@pytest.mark.parametrize('failure', ['counts', 'triggers', 'audit_count', 'audit_rows', 'findings'])
def test_failed_audit_returns_nonzero(monkeypatch, receipt_environment, failure, capsys):
    state, controls = receipt_environment
    if failure == 'counts': state['matches_expected_counts'] = False
    elif failure == 'triggers': controls['triggers'] = 8
    elif failure == 'audit_count': controls['sql_count'] = 9
    elif failure == 'audit_rows': controls['sql_rows'] = [{'invalid': 1}]
    else: state['findings'] = {'check': [{'invalid': 1}]}
    monkeypatch.setattr('sys.argv', ['preflight'])
    assert preflight.main() == 1
    assert json.loads(capsys.readouterr().out)['passed'] is False


def test_valid_receipt_can_be_saved(monkeypatch, receipt_environment, tmp_path, capsys):
    destination = tmp_path / 'receipt.json'
    monkeypatch.setattr('sys.argv', ['preflight', '--expected-sha', 'a'*40, '--output', str(destination)])
    assert preflight.main() == 0
    receipt = json.loads(destination.read_text())
    assert receipt['passed'] is True
    assert receipt['source_sha'] == 'a'*40
    assert receipt['sql_audit_row_counts'] == [0]*10
    assert receipt['database'] == 'receipt_test'
    assert 'password' not in capsys.readouterr().out.lower()


def test_wrong_source_stops_before_database(monkeypatch, receipt_environment):
    monkeypatch.setattr('sys.argv', ['preflight', '--expected-sha', 'b'*40])
    def unexpected():
        pytest.fail('Wrong source must be rejected before creating app/querying DB')
    monkeypatch.setattr(preflight, 'create_app', unexpected)
    with pytest.raises(SystemExit) as exc:
        preflight.main()
    assert exc.value.code == 2


def test_existing_receipt_is_not_overwritten(monkeypatch, receipt_environment, tmp_path):
    destination = tmp_path / 'receipt.json'
    destination.write_text('original evidence')
    monkeypatch.setattr('sys.argv', ['preflight', '--output', str(destination)])
    with pytest.raises(FileExistsError):
        preflight.main()
    assert destination.read_text() == 'original evidence'
