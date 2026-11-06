"""Read-only validation of this completed acceptance run; no DB credentials used."""
import hashlib
import json
import re
import socket
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = HERE/'run'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def closed(port):
    with socket.socket() as sock:
        sock.settimeout(.2)
        return sock.connect_ex(('127.0.0.1', port)) != 0


def log_text(path):
    data = path.read_bytes()
    # Windows PowerShell redirection uses UTF-16; Python evidence uses UTF-8.
    return data.decode('utf-16' if data.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig')


def verify():
    report = read(RUN/'results.json')
    assert report['success']
    assert report['source_sha'] == '2c01db2fe1d2d424f7dfe5b0a8192188d2c5fdc0'
    assert report['env_before'] is None and report['env_after'] is None
    assert not (ROOT/'.env').exists()
    assert read(RUN/'seed-before.json') == read(RUN/'seed-after.json')
    assert report['audit']['total'] == 1144 and report['audit']['matches_expected_counts']
    assert all(not rows for rows in report['audit']['findings'].values())
    assert report['cleanup']['success'] and closed(report['mysql_port'])
    changed = [name for name,digest in read(RUN/'source-sha256.json').items()
               if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != digest]
    assert not changed, changed
    counts, test_ids = {}, []
    for name in ['regression','windows-cleanup','mysql-ui']:
        suites = list(ET.parse(RUN/(name+'.xml')).getroot().iter('testsuite'))
        count = {k:sum(int(s.attrib.get(k,0)) for s in suites)
                 for k in ['tests','failures','errors','skipped']}
        assert count['failures'] == count['errors'] == count['skipped'] == 0
        count['passed'] = count['tests']
        counts[name] = count
        test_ids.extend((t.attrib['classname'],t.attrib['name'])
                        for s in suites for t in s.findall('testcase'))
    assert len(test_ids) == len(set(test_ids)), 'Overlapping test IDs across phases'
    assert len(test_ids) == 485
    windows = []
    for path in sorted((HERE/'windows-cleanup').glob('*/results.json')):
        result = read(path)
        assert result['mysql_cleanup']['success'] and closed(result['mysql_port'])
        assert result['env_unchanged']
        windows.append(dict(mode=result['cleanup_check'],port=result['mysql_port'],port_closed=True))
    assert {x['mode'] for x in windows} == {'success','error'}
    service = json.loads(subprocess.check_output(
        ['powershell','-NoProfile','-Command',
         "Get-Service MySQL84 | Select-Object Name,@{Name='Status';Expression={$_.Status.ToString()}} | ConvertTo-Json -Compress"],text=True))
    assert service['Status'] == 'Running'
    assert subprocess.run(['git','diff','--quiet',report['source_sha'],'--',
                           'clinic_app','database','tools','tests','requirements.txt','requirements-dev.txt'],cwd=ROOT).returncode == 0
    text_files = [p for p in HERE.rglob('*') if p.is_file() and p.suffix in {'.txt','.json','.xml','.md','.py'}]
    possible_private_password = [p.relative_to(HERE).as_posix() for p in text_files
        if re.search(r'(?<![0-9a-f])[0-9a-f]{48}(?![0-9a-f])',log_text(p))]
    assert not possible_private_password, possible_private_password
    result = dict(source_hashes_match=True,seed_rows_identical=True,seed_total=1144,
                  distinct_test_cases=len(test_ids),phases=counts,private_ports_closed=True,
                  windows_instances=windows,working_service=service,env_still_absent=True,
                  tracked_application_sql_tests_unchanged=True,private_password_literal_detected=False,
                  screenshot_count=len(list((RUN/'browser-artifacts').rglob('*.png'))))
    (HERE/'postflight.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    verify()
