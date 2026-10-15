"""Session-bound token for HTML forms; no third-party authentication system."""
import secrets
from flask import current_app, request, session
from werkzeug.exceptions import BadRequest


def csrf_token():
    if '_csrf' not in session:
        session['_csrf'] = secrets.token_hex(32)
    return session['_csrf']


def check_csrf():
    if request.method not in ('POST', 'PUT', 'PATCH', 'DELETE') or not current_app.config['CSRF_ENABLED']:
        return
    supplied = request.form.get('csrf_token', '')
    expected = session.get('_csrf', '')
    if not supplied or not expected or not secrets.compare_digest(supplied, expected):
        raise BadRequest('Phiên biểu mẫu không hợp lệ. Tải lại trang rồi thử lại.')
