import os
import tempfile
import pytest

from instadam.app import create_app, db

@pytest.fixture
def client():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
    client = app.test_client()
    yield client