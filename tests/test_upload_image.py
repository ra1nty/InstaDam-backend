import os
import shutil

import pytest
from sqlalchemy.exc import IntegrityError
from werkzeug.datastructures import FileStorage

from instadam.app import create_app, db
from instadam.config import Config
from instadam.models.project import Project
from instadam.models.project_permission import AccessTypeEnum, ProjectPermission
from instadam.models.user import PrivilegesEnum, User
from tests.conftest import TEST_MODE


@pytest.fixture
def local_client():
    if os.path.isdir(Config.STATIC_STORAGE_DIR):
        shutil.rmtree(Config.STATIC_STORAGE_DIR)
    app = create_app(TEST_MODE)
    with app.app_context():
        db.create_all()
        user = User(id=0, username='user1', email='email@illinois.edu',
                    privileges=PrivilegesEnum.ADMIN)
        user.set_password('TestTest1')
        project = Project(id=0, project_name='test/test', created_by=user.id)
        permission = ProjectPermission(access_type=AccessTypeEnum.READ_WRITE)
        permission.user_id = user.id
        permission.project_id = project.id
        user.project_permissions.append(permission)
        permission.project = project
        try:
            db.session.add(user)
            db.session.add(project)
            db.session.add(permission)
            db.session.flush()
        except IntegrityError:
            assert False
        db.session.commit()

        user = User(id=1, username='user2', email='email2@illinois.edu')
        user.set_password('TestTest1')
        permission = ProjectPermission(access_type=AccessTypeEnum.READ_ONLY)
        user.project_permissions.append(permission)
        permission.project = project

        try:
            db.session.add(user)
            db.session.add(permission)
        except IntegrityError:
            assert False
        db.session.commit()
    client = app.test_client()
    yield client


def test_upload_image(local_client):
    rv = local_client.post(
        '/login',
        json={'username': 'user1', 'password': 'TestTest1'},
        follow_redirects=True)

    assert '201 CREATED' == rv.status
    json_data = rv.get_json()
    assert 'access_token' in json_data

    access_token = json_data['access_token']

    with open('tests/cat.jpg', 'rb') as img:
        file = FileStorage(img)
        rv = local_client.post(
            '/image/upload/0', data={'image': file},
            headers={'Authorization': 'Bearer %s' % access_token})
        assert '200 OK' == rv.status
