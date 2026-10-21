"""Application factory for the clinic week-1 backend."""
import pymysql
from decimal import Decimal
from flask import Flask, render_template, request
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv
from .config import settings
from .db import close_db
from .security import check_csrf, csrf_token


def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__)
    app.config.from_mapping(settings())
    if test_config:
        app.config.update(test_config)
    if not app.config.get('SECRET_KEY'):
        raise RuntimeError('Cần đặt FLASK_SECRET_KEY trong .env trước khi chạy ứng dụng.')
    app.teardown_appcontext(close_db)
    app.before_request(check_csrf)
    app.jinja_env.globals['csrf_token'] = csrf_token
    app.jinja_env.filters['money'] = lambda v: f'{Decimal(v or 0):,.0f}'.replace(',', '.') + ' đ'
    from .routes import bp
    app.register_blueprint(bp)
    from .clinical_routes import bp as clinical_bp
    app.register_blueprint(clinical_bp)

    @app.errorhandler(HTTPException)
    def http_error(exc):
        return render_template('week1/error.html', status=exc.code, message=exc.description), exc.code

    @app.errorhandler(pymysql.MySQLError)
    def db_error(exc):
        # Log only the numeric code: exception strings may include host/username/form values.
        code = exc.args[0] if exc.args else None
        app.logger.error('MySQL operation failed; code=%s endpoint=%s', code, request.endpoint)
        if isinstance(exc, pymysql.OperationalError):
            if request.path == '/health/db':
                return {'status': 'unavailable'}, 503
            return render_template('week1/error.html', status=503,
                                   message='Không thể kết nối hoặc hoàn tất thao tác MySQL. Kiểm tra cấu hình và thử lại.'), 503
        return render_template('week1/error.html', status=500,
                               message='Không thể xử lý dữ liệu. Liên hệ người phụ trách để kiểm tra schema.'), 500

    @app.errorhandler(500)
    def server_error(_exc):
        return render_template('week1/error.html', status=500,
                               message='Có lỗi xử lý. Thao tác ghi chưa hoàn tất đã được hủy.'), 500

    return app
