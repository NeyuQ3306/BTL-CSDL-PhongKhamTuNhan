"""Server rendered demo forms plus stable JSON report contracts for integration."""
from datetime import date
from decimal import Decimal
import pymysql
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.exceptions import HTTPException, NotFound
from . import workflows, reports
from .db import fetch_all, fetch_one
from .validation import today_vn

bp = Blueprint('clinical', __name__)


def choices():
    return dict(patients=fetch_all('SELECT ma_benh_nhan,ho_ten FROM benh_nhan ORDER BY ma_benh_nhan'),
        doctors=fetch_all('SELECT ma_bac_si,ho_ten FROM bac_si ORDER BY ma_bac_si'),
        nurses=fetch_all('SELECT ma_y_ta,ho_ten FROM y_ta ORDER BY ma_y_ta'),
        diseases=fetch_all('SELECT ma_benh,ten_benh FROM benh ORDER BY ma_benh'),
        episodes=fetch_all("SELECT ma_dot,ma_benh_nhan,ma_benh FROM dot_dieu_tri WHERE trang_thai='Đang điều trị' ORDER BY ma_dot"),
        medicines=fetch_all('SELECT ma_thuoc,ten_thuoc,gia_hien_tai FROM thuoc ORDER BY ma_thuoc'))


def form_response(action, title, execute, success_endpoint, success_args=None, extra=None):
    values = request.form if request.method == 'POST' else request.args
    error, status = '', 200
    if request.method == 'POST':
        try:
            result = execute()
            flash('Đã lưu thành công.', 'success')
            args = success_args(result) if callable(success_args) else (success_args or {})
            return redirect(url_for(success_endpoint, **args), code=303)
        except HTTPException as exc:
            if exc.code not in (404, 409, 422):
                raise
            error, status = exc.description, exc.code
        except pymysql.IntegrityError:
            error, status = 'Mã đã tồn tại hoặc dữ liệu vi phạm ràng buộc. Không có thay đổi nào được lưu.', 409
    return render_template('week2/form.html', action=action, title=title, values=values,
                           error=error, choices=choices(), today=today_vn().isoformat(), **(extra or {})), status


@bp.route('/visits/new', methods=['GET','POST'])
def new_visit():
    return form_response('visit', 'Tiếp nhận và khám bệnh', lambda: workflows.create_visit(request.form),
                         'clinical.visit_detail', lambda result: dict(visit_id=result))


@bp.get('/visits/<visit_id>')
def visit_detail(visit_id):
    visit = fetch_one('''SELECT l.*,b.ho_ten FROM luot_den_kham l JOIN benh_nhan b
        ON b.ma_benh_nhan=l.ma_benh_nhan WHERE l.ma_luot=%s''', (visit_id,))
    if not visit:
        raise NotFound('Không tìm thấy lượt khám.')
    exams = fetch_all('''SELECT k.*,b.ten_benh,d.ma_bac_si,d.trang_thai,p.ma_don
        FROM lan_kham_benh k JOIN dot_dieu_tri d ON d.ma_dot=k.ma_dot JOIN benh b ON b.ma_benh=d.ma_benh
        LEFT JOIN don_thuoc p ON p.ma_lan_kham=k.ma_lan_kham WHERE k.ma_luot=%s ORDER BY k.ma_lan_kham''', (visit_id,))
    support = fetch_all('''SELECT h.*,y.ho_ten FROM ho_tro h JOIN y_ta y ON y.ma_y_ta=h.ma_y_ta
        WHERE h.ma_luot=%s ORDER BY h.ma_y_ta''', (visit_id,))
    return render_template('week2/visit.html', visit=visit, examinations=exams, support=support)


@bp.route('/visits/<visit_id>/examinations/new', methods=['GET','POST'])
def new_exam(visit_id):
    return form_response('exam', f'Khám thêm bệnh trong lượt {visit_id}', lambda: workflows.add_examination(visit_id, request.form),
                         'clinical.visit_detail', dict(visit_id=visit_id))


@bp.route('/visits/<visit_id>/support', methods=['GET','POST'])
def support(visit_id):
    return form_response('support', f'Ghi hỗ trợ cho lượt {visit_id}', lambda: workflows.record_support(visit_id, request.form),
                         'clinical.visit_detail', dict(visit_id=visit_id))


@bp.route('/visits/<visit_id>/close', methods=['GET','POST'])
def close_visit(visit_id):
    return form_response('close', f'Kết thúc lượt {visit_id}', lambda: workflows.close_visit(visit_id, request.form),
                         'clinical.visit_detail', dict(visit_id=visit_id))


@bp.route('/treatments/<episode_id>/cure', methods=['GET','POST'])
def cure(episode_id):
    return form_response('cure', f'Xác nhận khỏi — đợt {episode_id}', lambda: workflows.cure(episode_id, request.form),
                         'clinic.treatments')


@bp.route('/examinations/<exam_id>/prescription', methods=['GET','POST'])
def prescription(exam_id):
    def submit():
        ids, counts, usages = (request.form.getlist(k) for k in ['ma_thuoc','so_luong','lieu_dung'])
        if not len(ids) == len(counts) == len(usages):
            from .workflow_validation import invalid
            invalid('Các dòng thuốc không đầy đủ.')
        lines = [dict(ma_thuoc=i,so_luong=n,lieu_dung=u) for i,n,u in zip(ids,counts,usages) if i or n or u]
        return workflows.prescribe(exam_id, request.form, lines)
    return form_response('prescription', f'Kê đơn — lần khám {exam_id}', submit,
                         'clinical.prescription_detail', lambda result: dict(order_id=result))


@bp.get('/prescriptions/<order_id>')
def prescription_detail(order_id):
    order = fetch_one('SELECT * FROM don_thuoc WHERE ma_don=%s', (order_id,))
    if not order:
        raise NotFound('Không tìm thấy đơn thuốc.')
    rows = fetch_all('''SELECT c.*,t.ten_thuoc,t.don_vi_tinh,c.so_luong*c.don_gia_ban AS thanh_tien
        FROM chi_tiet_don_thuoc c JOIN thuoc t ON t.ma_thuoc=c.ma_thuoc
        WHERE c.ma_don=%s ORDER BY c.ma_thuoc''', (order_id,))
    return render_template('week2/prescription.html', order=order, rows=rows, total=sum(x['thanh_tien'] for x in rows))


def json_values(obj):
    if isinstance(obj, dict):
        return {k: json_values(v) for k,v in obj.items()}
    if isinstance(obj, list):
        return [json_values(v) for v in obj]
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, date):
        return obj.isoformat()
    return obj


@bp.get('/reports/<kind>')
def report(kind):
    builders = dict(diseases=reports.diseases, salaries=reports.salaries, revenue=reports.revenue)
    if kind == 'history':
        patient_id = request.args.get('patient_id', '').strip()
        if not patient_id:
            return render_template('week2/history_search.html', patients=choices()['patients'])
        data = reports.history(patient_id)
    elif kind in builders:
        data = builders[kind](request.args.get('month'))
    else:
        raise NotFound()
    if request.args.get('format') == 'json':
        return jsonify(json_values(data))
    if kind == 'history':
        return render_template('week1/history.html', **data)
    return render_template('week2/report.html', kind=kind, **data)
