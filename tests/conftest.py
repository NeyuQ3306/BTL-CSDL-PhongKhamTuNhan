import os
import pytest
from clinic_app import create_app


@pytest.fixture(scope='session')
def app():
    if os.getenv('RUN_MYSQL_TESTS') != '1':
        pytest.skip('Set RUN_MYSQL_TESTS=1 and point DB_NAME to a disposable *_test database')
    if not os.getenv('DB_NAME', '').endswith('_test'):
        pytest.fail('Refusing integration tests: DB_NAME must end with _test')
    return create_app({'TESTING': True, 'SECRET_KEY': 'disposable-test-session-key'})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def token(client):
    client.get('/patients/new')
    with client.session_transaction() as session:
        return session['_csrf']
