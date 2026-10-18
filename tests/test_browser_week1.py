"""Week-1 UI acceptance against real MySQL, including case-variant URLs."""
import os
import threading
from pathlib import Path
import pytest
from werkzeug.serving import make_server
from clinic_app.db import transaction


@pytest.mark.skipif(os.getenv('RUN_BROWSER_TESTS') != '1', reason='Enable RUN_BROWSER_TESTS and install Playwright Chromium')
@pytest.mark.parametrize('slug', ['patients', 'doctors', 'nurses'])
def test_browser_week1_crud(app, slug):
    from playwright.sync_api import sync_playwright, expect
    from clinic_app.entities import ENTITIES
    entity=ENTITIES[slug]
    key='UiW1'+slug[:3]
    fields={f.name:'Kiểm thử giao diện' for f in entity.fields}
    fields.update({entity.pk:key,'cmt':'000999777666','ngay_sinh':'2000-01-01',
                   'so_dien_thoai':'0901234567','tham_nien':'4'})
    server=make_server('127.0.0.1',0,app,threaded=True)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base=f'http://127.0.0.1:{server.server_port}'
    output=Path('test-artifacts/week1');output.mkdir(parents=True,exist_ok=True)
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch()
            page=browser.new_page(viewport={'width':1440,'height':1000},locale='vi-VN')
            page.goto(f'{base}/{slug}/new')
            for f in entity.fields:page.locator(f'[name="{f.name}"]').fill(fields[f.name])
            page.get_by_role('button',name='Thêm hồ sơ',exact=True).click()
            expect(page).to_have_url(f'{base}/{slug}/{key}')
            expect(page.get_by_text('000999777666',exact=True)).to_be_visible()
            page.screenshot(path=str(output/f'{slug}-created.png'),full_page=True)
            page.goto(f'{base}/{slug}/{key.lower()}/edit')
            expect(page.locator(f'[name="{entity.pk}"]')).to_have_value(key)
            page.locator('[name="ho_ten"]').fill('Đã sửa qua giao diện')
            page.get_by_role('button',name='Lưu thay đổi',exact=True).click()
            expect(page).to_have_url(f'{base}/{slug}/{key}')
            expect(page.get_by_role('heading',name='Đã sửa qua giao diện')).to_be_visible()
            page.screenshot(path=str(output/f'{slug}-edited.png'),full_page=True)
            page.locator('summary').click()
            page.locator('[name="confirm_delete"]').fill(key)
            page.get_by_role('button',name='Xác nhận xóa').click()
            expect(page).to_have_url(f'{base}/{slug}')
            expect(page.get_by_text('Đã xóa hồ sơ chưa phát sinh nghiệp vụ.',exact=True)).to_be_visible()
            page.screenshot(path=str(output/f'{slug}-deleted.png'),full_page=True)
            assert page.goto(f'{base}/{slug}/{key}').status==404
            browser.close()
    finally:
        server.shutdown();thread.join(timeout=5);server.server_close()
        with app.app_context():
            with transaction() as db, db.cursor() as c:
                c.execute(f'DELETE FROM {entity.table} WHERE {entity.pk}=%s',(key,))
