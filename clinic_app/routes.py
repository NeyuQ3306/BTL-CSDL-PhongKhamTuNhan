from math import ceil
from flask import Blueprint, request, render_template, redirect, url_for, flash
from werkzeug.exceptions import BadRequest, NotFound
import pymysql
from . import services
from .db import fetch_one
from .entities import ENTITIES
from .validation import validate

bp = Blueprint('clinic', __name__)


def entity_for(slug):
    if slug not in ENTITIES:
        raise NotFound()
    return ENTITIES[slug]


def database_form_error(exc):
    if exc.args[0] == 1062:
        return 'Mã hồ sơ hoặc CMT/CCCD đã tồn tại. Vui lòng kiểm tra lại.'
    return 'Dữ liệu vi phạm ràng buộc của cơ sở dữ liệu.'


@bp.get('/')
def home():
    return redirect(url_for('clinic.listing', slug='patients'))


@bp.get('/health')
def health():
    return {'status': 'ok'}


@bp.get('/health/db')
def health_db():
    fetch_one('SELECT 1 AS ok')
    return {'status': 'ok', 'database': 'mysql'}


@bp.get('/<slug>')
def listing(slug):
    entity = entity_for(slug)
    try:
        page = int(request.args.get('page', '1'))
        if page < 1 or page > 100000:
            raise ValueError
    except ValueError:
        raise BadRequest('Số trang phải là số nguyên dương, không vượt quá 100000.')
    q = request.args.get('q', '').strip()
    if len(q) > 100:
        raise BadRequest('Từ khóa tìm kiếm tối đa 100 ký tự.')
    rows, total = services.list_records(entity, q, page)
    return render_template('week1/list.html', entity=entity, rows=rows, q=q,
                           page=page, pages=max(1, ceil(total/20)), total=total)


@bp.route('/<slug>/new', methods=['GET', 'POST'])
def create(slug):
    entity = entity_for(slug)
    values, errors, form_error, status = {}, {}, '', 200
    if request.method == 'POST':
        values, errors = validate(entity, request.form)
        if errors:
            status = 422
        else:
            try:
                record_id = services.save_record(entity, values)
                flash('Đã thêm hồ sơ thành công.', 'success')
                return redirect(url_for('clinic.detail', slug=slug, record_id=record_id), code=303)
            except pymysql.IntegrityError as exc:
                form_error, status = database_form_error(exc), 409
    return render_template('week1/form.html', entity=entity, values=values, errors=errors,
                           form_error=form_error, editing=False), status


@bp.get('/<slug>/<record_id>')
def detail(slug, record_id):
    entity = entity_for(slug)
    return render_template('week1/detail.html', entity=entity,
                           record=services.get_record(entity, record_id), form_error='')


@bp.route('/<slug>/<record_id>/edit', methods=['GET', 'POST'])
def edit(slug, record_id):
    entity = entity_for(slug)
    record = services.get_record(entity, record_id)
    # The DB may match an alias with different letter case. Keep the stored PK.
    record_id = record[entity.pk]
    values, errors, form_error, status = record, {}, '', 200
    if request.method == 'POST':
        values, errors = validate(entity, request.form, fixed_id=record_id)
        if errors:
            status = 422
        else:
            try:
                services.save_record(entity, values, record_id)
                flash('Đã cập nhật hồ sơ.', 'success')
                return redirect(url_for('clinic.detail', slug=slug, record_id=record_id), code=303)
            except pymysql.IntegrityError as exc:
                form_error, status = database_form_error(exc), 409
    return render_template('week1/form.html', entity=entity, values=values, errors=errors,
                           form_error=form_error, editing=True), status


@bp.post('/<slug>/<record_id>/delete')
def delete(slug, record_id):
    entity = entity_for(slug)
    record = services.get_record(entity, record_id)
    record_id = record[entity.pk]
    if request.form.get('confirm_delete') != record_id:
        raise BadRequest('Bạn chưa xác nhận đúng mã hồ sơ cần xóa.')
    try:
        services.delete_record(entity, record_id)
    except pymysql.IntegrityError as exc:
        if exc.args[0] != 1451:
            raise
        return render_template('week1/detail.html', entity=entity, record=record,
                               form_error='Không thể xóa: hồ sơ đang được lịch sử khám hoặc hỗ trợ tham chiếu.'), 409
    flash('Đã xóa hồ sơ chưa phát sinh nghiệp vụ.', 'success')
    return redirect(url_for('clinic.listing', slug=slug), code=303)


@bp.get('/visits')
def visits():
    return render_template('week1/visits.html', rows=services.visits())


@bp.get('/treatments')
def treatments():
    return render_template('week1/treatments.html', rows=services.treatments())


@bp.get('/patients/<record_id>/history')
def history(record_id):
    from .reports import history as full_history
    return render_template('week1/history.html', **full_history(record_id))
