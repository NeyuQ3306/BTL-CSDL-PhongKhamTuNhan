"""Login and fail-closed role checks. Credentials live in optional app_user table."""
import re
import time
from collections import OrderedDict
from datetime import timedelta
import click
import pymysql
from flask import Blueprint, current_app, g, session, request, redirect, url_for, render_template, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from .db import fetch_one, fetch_all, transaction

bp = Blueprint('auth', __name__, url_prefix='/auth')
ROLES = {'admin': 'Quản trị viên', 'reception': 'Tiếp nhận', 'doctor': 'Bác sĩ', 'nurse': 'Y tá'}
DUMMY_HASH = generate_password_hash('not-a-real-login-password')
# Per-process IP cap supplements persistent per-account failed-login lockout.
_attempts = OrderedDict()
SCHEMA = '''CREATE TABLE IF NOT EXISTS app_user (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 username VARCHAR(64) CHARACTER SET ascii COLLATE ascii_general_ci NOT NULL UNIQUE,
 password_hash VARCHAR(255) NOT NULL,
 role VARCHAR(16) NOT NULL,
 doctor_id VARCHAR(12) NULL,
 nurse_id VARCHAR(12) NULL,
 active BOOLEAN NOT NULL DEFAULT TRUE,
 version INT UNSIGNED NOT NULL DEFAULT 1,
 failed_logins INT UNSIGNED NOT NULL DEFAULT 0,
 locked_until DATETIME NULL,
 CONSTRAINT fk_app_user_doctor FOREIGN KEY (doctor_id) REFERENCES bac_si(ma_bac_si),
 CONSTRAINT fk_app_user_nurse FOREIGN KEY (nurse_id) REFERENCES y_ta(ma_y_ta),
 CONSTRAINT ck_app_user_role CHECK (
   (role IN ('admin','reception') AND doctor_id IS NULL AND nurse_id IS NULL) OR
   (role='doctor' AND doctor_id IS NOT NULL AND nurse_id IS NULL) OR
   (role='nurse' AND nurse_id IS NOT NULL AND doctor_id IS NULL))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci'''


def enabled():
    return current_app.config.get('AUTH_ENABLED', True)


def can(endpoint, **args):
    """UI capability hints; server separately validates record ownership."""
    if not enabled():
        return True
    user = g.get('user')
    if not user:
        return False
    role = user['role']
    if role == 'admin':
        return True
    if endpoint in ('clinic.home', 'clinic.health', 'clinic.health_db'):
        return True
    if endpoint.startswith('auth.'):
        return endpoint in ('auth.login', 'auth.logout')
    if endpoint in ('clinic.listing', 'clinic.detail'):
        return args.get('slug') == 'patients'
    if endpoint in ('clinic.create', 'clinic.edit', 'clinic.delete'):
        return role == 'reception' and args.get('slug') == 'patients'
    if endpoint in ('clinic.visits', 'clinical.visit_detail'):
        return True
    if endpoint in ('clinic.history', 'clinic.treatments', 'clinical.prescription_detail'):
        return role in ('doctor', 'nurse')
    if endpoint == 'clinical.new_visit':
        return role in ('reception', 'doctor')
    if endpoint in ('clinical.new_exam', 'clinical.cure', 'clinical.prescription'):
        return role == 'doctor'
    if endpoint == 'clinical.support':
        return role == 'nurse'
    if endpoint == 'clinical.close_visit':
        return role == 'reception'
    return False


def own_doctor(code):
    return not enabled() or g.user['role'] == 'admin' or (
        g.user['role'] == 'doctor' and code.casefold() == g.user['doctor_id'].casefold())


def require_doctor(code):
    if not own_doctor(code):
        abort(403, 'Đợt điều trị thuộc bác sĩ khác.')


def authorize():
    g.user = None
    if not enabled():
        return
    endpoint = request.endpoint or ''
    if endpoint == 'static' or endpoint == 'clinic.health':
        return
    if session.get('user_id'):
        try:
            user = fetch_one('SELECT id,username,role,doctor_id,nurse_id,active,version FROM app_user WHERE id=%s', (session['user_id'],))
        except pymysql.ProgrammingError as exc:
            if exc.args[0] != 1146:
                raise
            user = None
        if user and user['active'] and user['version'] == session.get('user_version'):
            g.user = user
        else:
            session.clear()
    if endpoint == 'auth.login':
        return
    if not g.user:
        if request.path.startswith('/api/') or request.args.get('format') == 'json' or request.method != 'GET':
            return {'error': 'Cần đăng nhập.'}, 401
        return redirect(url_for('auth.login'))
    if not can(endpoint, **(request.view_args or {})):
        abort(403, 'Tài khoản không có quyền sử dụng chức năng này.')
    # Reject forged clinical IDs before rendering a form or executing a write.
    args = request.view_args or {}
    if g.user['role'] == 'doctor':
        row = None
        if endpoint == 'clinical.cure':
            row = fetch_one('SELECT ma_bac_si FROM dot_dieu_tri WHERE ma_dot=%s', (args['episode_id'],))
        elif endpoint == 'clinical.prescription':
            row = fetch_one('SELECT d.ma_bac_si FROM lan_kham_benh k JOIN dot_dieu_tri d ON d.ma_dot=k.ma_dot WHERE k.ma_lan_kham=%s', (args['exam_id'],))
        if row:
            require_doctor(row['ma_bac_si'])
        if endpoint in ('clinical.new_visit', 'clinical.new_exam') and request.method == 'POST':
            if request.form.get('che_do_dot') == 'new':
                require_doctor(request.form.get('ma_bac_si', ''))
            else:
                row = fetch_one('SELECT ma_bac_si FROM dot_dieu_tri WHERE ma_dot=%s', (request.form.get('ma_dot'),))
                if row:
                    require_doctor(row['ma_bac_si'])
    if endpoint == 'clinical.support' and g.user['role'] == 'nurse':
        supplied = request.form.get('ma_y_ta') if request.method == 'POST' else request.args.get('ma_y_ta')
        if supplied and supplied.casefold() != g.user['nurse_id'].casefold():
            abort(403, 'Chỉ được cập nhật hỗ trợ dưới mã y tá của mình.')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if g.get('user'):
        return redirect(url_for('clinic.home'))
    error = ''
    status = 200
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        # Do not trust forwarded headers from clients for rate limiting.
        ip = request.remote_addr or 'unknown'
        now = time.monotonic()
        count, until = _attempts.get(ip, (0, now + 900))
        if now >= until:
            count, until = 0, now + 900
        _attempts[ip] = (count + 1, until)
        _attempts.move_to_end(ip)
        while len(_attempts) > 4096:
            _attempts.popitem(last=False)
        if count >= 20:
            return render_template('auth/login.html', error='Thử quá nhiều lần. Vui lòng đợi 15 phút.'), 429
        try:
            user = fetch_one('SELECT *, (locked_until IS NOT NULL AND locked_until>NOW()) AS locked FROM app_user WHERE username=%s', (username,))
        except pymysql.ProgrammingError as exc:
            if exc.args[0] != 1146:
                raise
            return render_template('auth/login.html', error='Chưa khởi tạo tài khoản. Chạy lệnh init-auth theo hướng dẫn.'), 503
        valid = check_password_hash(user['password_hash'] if user else DUMMY_HASH, password[:1024])
        if user and user['active'] and not user['locked'] and valid and len(password) <= 1024:
            with transaction() as db, db.cursor() as cur:
                cur.execute('UPDATE app_user SET failed_logins=0,locked_until=NULL WHERE id=%s', (user['id'],))
            session.clear()
            session['user_id'] = user['id']
            session['user_version'] = user['version']
            session.permanent = True
            return redirect(url_for('clinic.home'), code=303)
        if user and not user['locked']:
            with transaction() as db, db.cursor() as cur:
                cur.execute('''UPDATE app_user SET failed_logins=IF(locked_until IS NOT NULL AND locked_until<=NOW(),1,failed_logins+1),
                    locked_until=IF(failed_logins>=5,DATE_ADD(NOW(),INTERVAL 15 MINUTE),NULL) WHERE id=%s''', (user['id'],))
        error, status = 'Thông tin đăng nhập không đúng hoặc tài khoản tạm thời bị khóa.', 401
    return render_template('auth/login.html', error=error), status


@bp.post('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'), code=303)


def checked_account(data, new=False):
    username = data.get('username', '').strip().lower()
    role = data.get('role')
    password = data.get('password', '')
    if not re.fullmatch(r'[a-z0-9_.-]{3,64}', username) or role not in ROLES:
        raise ValueError('Tên đăng nhập cần 3–64 ký tự a-z, số, _, . hoặc -; chọn vai trò hợp lệ.')
    if (new or password) and not 6 <= len(password) <= 36:
        raise ValueError('Mật khẩu cần từ 6 đến 36 ký tự.')
    doctor = data.get('doctor_id', '').strip() if role == 'doctor' else None
    nurse = data.get('nurse_id', '').strip() if role == 'nurse' else None
    for value, table, key in ((doctor, 'bac_si', 'ma_bac_si'), (nurse, 'y_ta', 'ma_y_ta')):
        if value is not None and not fetch_one(f'SELECT {key} FROM {table} WHERE {key}=%s', (value,)):
            raise ValueError('Cần liên kết tài khoản với hồ sơ nhân sự hợp lệ.')
    return username, role, doctor, nurse, password


@bp.route('/users', methods=['GET', 'POST'])
def users():
    error, status = '', 200
    if request.method == 'POST':
        try:
            user_id = request.form.get('id', '')
            username, role, doctor, nurse, password = checked_account(request.form, new=not user_id)
            active = request.form.get('active') == '1'
            with transaction() as db, db.cursor() as cur:
                # Serialize admin changes so concurrent requests cannot remove the last admin.
                cur.execute('SELECT id FROM app_user ORDER BY id FOR UPDATE')
                cur.fetchall()
                if user_id:
                    cur.execute('SELECT * FROM app_user WHERE id=%s', (user_id,))
                    old = cur.fetchone()
                    if not old:
                        raise ValueError('Tài khoản không tồn tại.')
                    if old['id'] == g.user['id'] and (role != 'admin' or not active):
                        raise ValueError('Không thể tự hạ quyền hoặc khóa tài khoản admin đang sử dụng.')
                    cur.execute("SELECT COUNT(*) AS n FROM app_user WHERE role='admin' AND active=1 AND id<>%s", (user_id,))
                    if not cur.fetchone()['n'] and (role != 'admin' or not active) and old['role'] == 'admin' and old['active']:
                        raise ValueError('Phải giữ ít nhất một admin hoạt động.')
                    cur.execute('''UPDATE app_user SET username=%s,role=%s,doctor_id=%s,nurse_id=%s,active=%s,
                        password_hash=%s,version=version+1,failed_logins=0,locked_until=NULL WHERE id=%s''',
                        (username, role, doctor, nurse, active, generate_password_hash(password) if password else old['password_hash'], user_id))
                    if old['id'] == g.user['id']:
                        session['user_version'] = old['version'] + 1
                else:
                    cur.execute('INSERT INTO app_user (username,password_hash,role,doctor_id,nurse_id,active) VALUES (%s,%s,%s,%s,%s,%s)',
                                (username, generate_password_hash(password), role, doctor, nurse, active))
            flash('Đã lưu tài khoản. Thay đổi quyền hoặc mật khẩu sẽ kết thúc các phiên đăng nhập cũ.', 'success')
            return redirect(url_for('auth.users'), code=303)
        except ValueError as exc:
            error, status = str(exc), 422
        except pymysql.IntegrityError:
            error, status = 'Tên đăng nhập đã tồn tại hoặc hồ sơ nhân sự không hợp lệ.', 409
    return render_template('auth/users.html', error=error, roles=ROLES,
        users=fetch_all('SELECT id,username,role,doctor_id,nurse_id,active FROM app_user ORDER BY id'),
        doctors=fetch_all('SELECT ma_bac_si,ho_ten FROM bac_si ORDER BY ma_bac_si'),
        nurses=fetch_all('SELECT ma_y_ta,ho_ten FROM y_ta ORDER BY ma_y_ta')), status


@bp.post('/users/<int:user_id>/delete')
def delete_user(user_id):
    with transaction() as db, db.cursor() as cur:
        # Match the lock order used by account editing, including concurrent admins.
        cur.execute('SELECT id FROM app_user ORDER BY id FOR UPDATE')
        cur.fetchall()
        cur.execute('SELECT id,username,role,active FROM app_user WHERE id=%s', (user_id,))
        user = cur.fetchone()
        if not user:
            abort(404, 'Tài khoản không còn tồn tại.')
        if user['id'] == g.user['id']:
            abort(422, 'Không thể xóa tài khoản admin đang đăng nhập.')
        if request.form.get('confirm_username', '') != user['username']:
            abort(422, 'Nhập đúng tên đăng nhập để xác nhận xóa tài khoản.')
        if user['role'] == 'admin' and user['active']:
            cur.execute("SELECT COUNT(*) AS n FROM app_user WHERE role='admin' AND active=1 AND id<>%s", (user_id,))
            if not cur.fetchone()['n']:
                abort(422, 'Phải giữ ít nhất một admin hoạt động.')
        cur.execute('DELETE FROM app_user WHERE id=%s', (user_id,))
    flash('Đã xóa tài khoản. Các phiên của tài khoản này hết hiệu lực; hồ sơ nhân sự và dữ liệu khám được giữ nguyên.', 'success')
    return redirect(url_for('auth.users'), code=303)


def init_app(app):
    if not app.config.get('AUTH_ENABLED', True) and not app.testing:
        raise RuntimeError('Chỉ được tắt đăng nhập trong cấu hình kiểm thử.')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
    app.register_blueprint(bp)
    app.before_request(authorize)
    app.jinja_env.globals.update(can=can, own_doctor=own_doctor)
    app.context_processor(lambda: {'current_user': g.get('user'), 'can': can, 'own_doctor': own_doctor, 'role_names': ROLES})

    @app.cli.command('init-auth')
    @click.option('--username', prompt='Tên đăng nhập admin')
    @click.password_option(confirmation_prompt=True)
    def init_auth(username, password):
        """Create optional account table and the first admin, without touching clinical data."""
        username = username.strip().lower()
        if not re.fullmatch(r'[a-z0-9_.-]{3,64}', username) or not 6 <= len(password) <= 36:
            raise click.ClickException('Tên tài khoản không hợp lệ hoặc mật khẩu không đủ 6–36 ký tự.')
        from .db import get_db
        db = get_db()
        with db.cursor() as cur:
            cur.execute(SCHEMA)
        with db.cursor() as cur:
            cur.execute("SELECT GET_LOCK(CONCAT('clinic-auth:',DATABASE()),10) AS acquired")
            if not cur.fetchone()['acquired']:
                raise click.ClickException('Một tiến trình khác đang khởi tạo tài khoản.')
        try:
            with transaction() as db, db.cursor() as cur:
                cur.execute("SELECT id FROM app_user WHERE role='admin' AND active=1 FOR UPDATE")
                if cur.fetchone():
                    raise click.ClickException('Admin đã tồn tại. Dùng trang quản lý tài khoản; không ghi đè mật khẩu.')
                cur.execute("INSERT INTO app_user (username,password_hash,role) VALUES (%s,%s,'admin')", (username, generate_password_hash(password)))
        finally:
            with db.cursor() as cur:
                cur.execute("SELECT RELEASE_LOCK(CONCAT('clinic-auth:',DATABASE()))")
        click.echo('Đã tạo admin. Đăng nhập để tạo tài khoản tiếp nhận, bác sĩ và y tá.')
