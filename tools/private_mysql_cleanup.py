"""Stop only a private instance identified by executable AND exact datadir."""
import os
import socket
import subprocess
import time
import psutil


def normalized(path):
    return os.path.normcase(os.path.realpath(path))


def matches_instance(process, executable, datadir):
    try:
        if normalized(process.exe()) != normalized(executable):
            return False
        args = process.cmdline()
        for i, arg in enumerate(args):
            if arg.lower().startswith('--datadir='):
                return normalized(arg.split('=', 1)[1]) == normalized(datadir)
            if arg.lower() == '--datadir' and i + 1 < len(args):
                return normalized(args[i + 1]) == normalized(datadir)
    except (psutil.Error, OSError):
        pass
    return False


def instance_processes(executable, datadir):
    return [p for p in psutil.process_iter() if matches_instance(p, executable, datadir)]


def port_open(port):
    with socket.socket() as sock:
        sock.settimeout(.2)
        return sock.connect_ex(('127.0.0.1', port)) == 0


def stop_private_mysql(proc, db, executable, datadir, port, timeout=10):
    result = dict(shutdown_requested=False, fallback_pids=[], errors=[])
    if db is not None:
        try:
            with db.cursor() as cursor:
                cursor.execute('SELECT @@datadir AS datadir, @@port AS port')
                identity = cursor.fetchone()
                if (not identity or normalized(identity['datadir']) != normalized(datadir)
                        or int(identity['port']) != port):
                    raise ValueError('Private connection identity mismatch')
                cursor.execute('SHUTDOWN')
            result['shutdown_requested'] = True
        except Exception as exc:
            # Only the type is recorded: DB exception strings may contain credentials.
            result['errors'].append(type(exc).__name__)
        finally:
            try:
                db.close()
            except Exception as exc:
                result['errors'].append(type(exc).__name__)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if proc is not None:
            proc.poll()  # reap a launcher even when a child owns the listening port
        if not instance_processes(executable, datadir) and not port_open(port):
            break
        time.sleep(.1)
    owned = instance_processes(executable, datadir)
    for process in owned:
        try:
            if matches_instance(process, executable, datadir):
                process.terminate()
                result['fallback_pids'].append(process.pid)
        except psutil.Error as exc:
            result['errors'].append(type(exc).__name__)
    _, alive = psutil.wait_procs(owned, timeout=timeout)
    for process in alive:
        try:
            if matches_instance(process, executable, datadir):
                process.kill()
        except psutil.Error as exc:
            result['errors'].append(type(exc).__name__)
    psutil.wait_procs(alive, timeout=timeout)
    if proc is not None:
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            result['errors'].append('LauncherTimeout')
    result['remaining_pids'] = [p.pid for p in instance_processes(executable, datadir)]
    result['port_closed'] = not port_open(port)
    result['launcher_exited'] = proc is None or proc.poll() is not None
    result['success'] = (not result['remaining_pids'] and result['port_closed'] and result['launcher_exited'])
    return result
