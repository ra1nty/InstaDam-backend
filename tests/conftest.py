import pytest

from instadam.app import create_app, db

TEST_MODE = 'development'


@pytest.fixture
def client():
    app = create_app(TEST_MODE)
    with app.app_context():
        db.create_all()
    client = app.test_client()
    yield client
