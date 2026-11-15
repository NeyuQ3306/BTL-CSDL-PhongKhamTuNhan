"""Real template rendering plus desktop/mobile reveal-control browser checks."""
import os
from pathlib import Path
import pytest
from flask import g, render_template
from clinic_app import create_app

ROOT = Path(__file__).resolve().parents[1]


def auth_markup(kind):
    app = create_app({'TESTING': True, 'SECRET_KEY': 'password-control-test'})
    with app.test_request_context('/auth/login' if kind == 'login' else '/auth/users'):
        if kind == 'login':
            g.user = None
            return render_template('auth/login.html', error='')
        g.user = dict(id=1, username='admin', role='admin')
        users = [dict(id=1,username='admin',role='admin',active=1),
                 dict(id=2,username='reception',role='reception',active=1)]
        return render_template('auth/users.html', error='', users=users, doctors=[], nurses=[],
                               roles={'admin':'Quản trị viên','reception':'Tiếp nhận'})


def test_all_password_inputs_have_independent_controls():
    for kind, ids in [('login',['password']),('users',['password-1','password-2','new-password'])]:
        html = auth_markup(kind)
        for id in ids:
            assert f'aria-controls="{id}"' in html
        assert 'password-visibility.js' in html
        assert html.count('data-password-field') == len(ids)
        assert html.count('class="password-toggle"') == len(ids)


@pytest.mark.parametrize('kind', ['login','users'])
@pytest.mark.parametrize('width', [390,1280])
def test_browser_reveal_stays_available(kind,width):
    if os.getenv('RUN_BROWSER_TESTS') != '1':
        pytest.skip('Set RUN_BROWSER_TESTS=1 with Playwright Chromium installed')
    sync = pytest.importorskip('playwright.sync_api')
    with sync.sync_playwright() as p:
        browser=p.chromium.launch()
        page=browser.new_page(viewport={'width':width,'height':900})
        page.set_content(auth_markup(kind))
        page.add_style_tag(path=str(ROOT/'clinic_app/static/week1.css'))
        page.locator('details.account-editor').evaluate_all('(items) => items.forEach(item => item.open = true)')
        page.add_script_tag(path=str(ROOT/'clinic_app/static/password-visibility.js'))
        page.evaluate("document.addEventListener('submit', e => { e.preventDefault(); window.unexpectedSubmit = true; })")
        fields=page.locator('[data-password-field]')
        for i in range(fields.count()):
            field=fields.nth(i); input=field.locator('input'); button=field.locator('button')
            assert button.is_visible()
            input.fill('test123')
            for _ in range(5):
                button.click()
                assert input.get_attribute('type')=='text'
                assert button.get_attribute('aria-pressed')=='true'
                assert input.input_value()=='test123'
                page.locator('h1').click()
                assert button.is_visible()
                button.click()
                assert input.get_attribute('type')=='password'
            button.focus(); button.press('Space')
            assert input.get_attribute('type')=='text'
            input.fill('')
            assert input.get_attribute('type')=='password' and button.is_visible()
            input.evaluate("input => { input.value = 'autofill123'; }")
            button.click()
            assert input.get_attribute('type')=='text' and input.input_value()=='autofill123'
            box=button.bounding_box(); ibox=input.bounding_box()
            assert box['x']>=ibox['x'] and box['x']+box['width']<=ibox['x']+ibox['width']+1
        assert not page.evaluate('Boolean(window.unexpectedSubmit)')
        page.evaluate("window.dispatchEvent(new Event('pagehide'))")
        for i in range(fields.count()):
            assert fields.nth(i).locator('input').get_attribute('type')=='password'
        browser.close()
