import filecmp
import os
import shutil

import pytest
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

        user = User(username='user1', email='email@illinois.edu',
                    privileges=PrivilegesEnum.ADMIN)
        user.set_password('TestTest1')
        db.session.add(user)
        db.session.flush()
        db.session.commit()

        project = Project(project_name='test/test', created_by=user.id)
        db.session.add(project)
        db.session.flush()
        db.session.commit()

        permission = ProjectPermission(access_type=AccessTypeEnum.READ_WRITE)
        user.project_permissions.append(permission)
        project.permissions.append(permission)

        user = User(username='user2', email='email2@illinois.edu')
        user.set_password('TestTest1')
        db.session.add(user)
        db.session.flush()
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
            '/image/upload/1', data={'image': file},
            headers={'Authorization': 'Bearer %s' % access_token})
        assert '200 OK' == rv.status
        json_data = rv.get_json()
        assert 'msg' in json_data
        assert 'Image added successfully' == json_data['msg']

    storage_path = os.path.join(Config.STATIC_STORAGE_DIR, '1')
    assert os.path.isdir(storage_path)
    files = os.listdir(storage_path)
    assert 1 == len(files)
    saved_file = files[0]
    assert filecmp.cmp('tests/cat.jpg', os.path.join(storage_path, saved_file))
