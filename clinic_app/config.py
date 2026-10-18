"""Environment configuration. No connection is opened while importing modules."""
import os


def settings():
    return {
        'SECRET_KEY': os.getenv('FLASK_SECRET_KEY'),
        'DB_HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'DB_PORT': int(os.getenv('DB_PORT', '3306')),
        'DB_USER': os.getenv('DB_USER', 'clinic_app'),
        'DB_PASSWORD': os.getenv('DB_PASSWORD', ''),
        'DB_NAME': os.getenv('DB_NAME', 'clinic_project1'),
        'DB_CONNECT_TIMEOUT': 5,
        'DB_READ_TIMEOUT': 10,
        'SESSION_COOKIE_HTTPONLY': True,
        'SESSION_COOKIE_SAMESITE': 'Lax',
        'SESSION_COOKIE_SECURE': os.getenv('COOKIE_SECURE', '').lower() == 'true',
        'MAX_CONTENT_LENGTH': 64 * 1024,
        'CSRF_ENABLED': True,
    }
