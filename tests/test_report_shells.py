"""Integrated reporting must dispatch exactly once and preserve the navigation hub."""
from decimal import Decimal
import pytest
from clinic_app import create_app, reports

@pytest.fixture
def report_client():
    return create_app({'TESTING': True, 'SECRET_KEY': 'report-test-session'}).test_client()

@pytest.mark.parametrize('kind',['diseases','salaries','revenue'])
def test_integrated_report_dispatch(monkeypatch,report_client,kind):
    calls=[]
    def build(month):
        calls.append(month)
        data=dict(month=month,total=Decimal(123))
        if kind=='diseases': data.update(rows=[])
        elif kind=='salaries': data.update(doctors=[],nurses=[])
        else: data.update(consultation=Decimal(100),medicine=Decimal(23))
        return data
    monkeypatch.setattr(reports,kind,build)
    response=report_client.get('/reports/'+kind+'?month=2001-02&format=json')
    assert response.status_code==200
    assert response.json['total']=='123'
    assert calls==['2001-02']
    assert report_client.get('/reports/'+kind+'?month=2001-02').status_code==200

@pytest.mark.parametrize('month',['2026-13','0000-01','26-10','','<script>'])
def test_bad_month_rejected_before_query(report_client,month):
    assert report_client.get('/reports/revenue',query_string={'month':month}).status_code==400

def test_hub_and_single_report_url(report_client):
    assert report_client.get('/reports').status_code==200
    rules=[r for r in report_client.application.url_map.iter_rules() if r.rule.startswith('/reports/<')]
    assert len(rules)==1
    assert report_client.get('/reports/unknown').status_code==404
