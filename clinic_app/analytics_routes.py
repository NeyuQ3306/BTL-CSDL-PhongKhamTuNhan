"""Stable JSON contract for Vuong's R01–R07 tables/charts. No template changes."""
import pymysql
from flask import Blueprint, current_app, jsonify, request
from werkzeug.exceptions import HTTPException
from . import analytics

bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')


@bp.get('')
def all_reports():
    return jsonify(analytics.build(analytics.filters(request.args)))


@bp.get('/<report_id>')
def one_report(report_id):
    values = analytics.filters(request.args, report_id)
    return jsonify(analytics.build(values, report_id))


@bp.errorhandler(HTTPException)
def http_error(exc):
    return jsonify(error=exc.description), exc.code


@bp.errorhandler(pymysql.MySQLError)
def database_error(exc):
    code = exc.args[0] if exc.args else None
    current_app.logger.error('Analytics MySQL failed; code=%s endpoint=%s', code, request.endpoint)
    status = 503 if isinstance(exc, pymysql.OperationalError) else 500
    return jsonify(error='Không thể lấy báo cáo MySQL. Kiểm tra kết nối và thử lại.'), status


@bp.errorhandler(500)
def server_error(_exc):
    return jsonify(error='Không thể xử lý báo cáo. Liên hệ người phụ trách.'), 500
