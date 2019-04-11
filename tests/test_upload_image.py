import filecmp
import os
import shutil
import time

import pytest
from werkzeug.datastructures import FileStorage

from instadam.app import create_app, db
from instadam.config import Config
from instadam.models.project import Project
from instadam.models.project_permission import AccessTypeEnum, ProjectPermission
from instadam.models.user import User
from tests.conftest import TEST_MODE


@pytest.fixture
def local_client():
    if os.path.isdir(Config.STATIC_STORAGE_DIR):
        shutil.rmtree(Config.STATIC_STORAGE_DIR)
    app = create_app(TEST_MODE)
    with app.app_context():
        db.reflect()
        db.drop_all()
        db.create_all()

        user = User(username='test_upload_user1', email='email@test_upload.com')
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

        user = User(username='test_upload_user2',
                    email='email2@test_upload.com')
        user.set_password('TestTest1')
        permission = ProjectPermission(access_type=AccessTypeEnum.READ_ONLY)
        user.project_permissions.append(permission)
        project.permissions.append(permission)
        db.session.add(user)
        db.session.flush()
        db.session.commit()

    client = app.test_client()
    yield client


def successful_login(client, username, password):
    rv = client.post(
        '/login',
        json={'username': username, 'password': password},
        follow_redirects=True)

    assert '201 CREATED' == rv.status
    json_data = rv.get_json()
    assert 'access_token' in json_data

    return json_data['access_token']


def test_upload_image(local_client):
    access_token = successful_login(local_client, 'test_upload_user1',
                                    'TestTest1')

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


def test_upload_image_fail_1(local_client):
    access_token = successful_login(local_client, 'test_upload_user1',
                                    'TestTest1')

    with open('tests/cat.jpg', 'rb') as img:
        file = FileStorage(img)
        rv = local_client.post(
            '/image/upload/0', data={'image': file},
            headers={'Authorization': 'Bearer %s' % access_token})
        assert '401 UNAUTHORIZED' == rv.status
        json_data = rv.get_json()
        assert 'msg' in json_data

    storage_path = os.path.join(Config.STATIC_STORAGE_DIR, '0')
    assert not os.path.isdir(storage_path)


def test_upload_image_fail_2(local_client):
    access_token = successful_login(local_client, 'test_upload_user2',
                                    'TestTest1')

    with open('tests/cat.jpg', 'rb') as img:
        file = FileStorage(img)
        rv = local_client.post(
            '/image/upload/1', data={'image': file},
            headers={'Authorization': 'Bearer %s' % access_token})
        assert '401 UNAUTHORIZED' == rv.status
        json_data = rv.get_json()
        assert 'msg' in json_data


def test_upload_image_fail_3(local_client):
    access_token = successful_login(local_client, 'test_upload_user1',
                                    'TestTest1')

    with open('tests/cat.jpg', 'rb') as img:
        file = FileStorage(img)
        rv = local_client.post(
            '/image/upload/1', data={'file': file},
            headers={'Authorization': 'Bearer %s' % access_token})
        assert '400 BAD REQUEST' == rv.status
        json_data = rv.get_json()
        assert 'msg' in json_data


def test_upload_image_fail_4(local_client):
    access_token = successful_login(local_client, 'test_upload_user1',
                                    'TestTest1')

    with open('tests/__init__.py', 'rb') as fd:
        file = FileStorage(fd)
        rv = local_client.post(
            '/image/upload/1', data={'image': file},
            headers={'Authorization': 'Bearer %s' % access_token})
        assert '415 UNSUPPORTED MEDIA TYPE' == rv.status
        json_data = rv.get_json()
        assert 'msg' in json_data


def test_upload_zip(local_client):
    access_token = successful_login(local_client, 'test_upload_user1',
                                    'TestTest1')
    with open('tests/test.zip', 'rb') as fd:
        file = FileStorage(fd)
        rv = local_client.post(
            '/image/upload/zip/1', data={'zip': file},
            headers={'Authorization': 'Bearer %s' % access_token})
        assert '200 OK' == rv.status
        json_data = rv.get_json()
        assert 'msg' in json_data
        assert 'Zip uploaded successfully, please wait for unzip' == json_data[
            'msg']

    time.sleep(1)

    storage_path = os.path.join(Config.STATIC_STORAGE_DIR, '1')
    assert os.path.isdir(storage_path)
    files = os.listdir(storage_path)
    assert 2 == len(files)
    assert filecmp.cmp(os.path.join(storage_path, files[0]),
                       os.path.join(storage_path, files[1]))
    assert filecmp.cmp(os.path.join(storage_path, files[0]), 'tests/cat.jpg')


def test_upload_zip_failed(local_client):
    access_token = successful_login(local_client, 'test_upload_user1',
                                    'TestTest1')
    with open('tests/cat.jpg', 'rb') as fd:
        file = FileStorage(fd)
        rv = local_client.post(
            '/image/upload/zip/1', data={'zip': file},
            headers={'Authorization': 'Bearer %s' % access_token})
        assert '415 UNSUPPORTED MEDIA TYPE' == rv.status


def test_upload_zip_failed2(local_client):
    access_token = successful_login(local_client, 'test_upload_user1',
                                    'TestTest1')
    with open('tests/cat.jpg', 'rb') as fd:
        file = FileStorage(fd)
        rv = local_client.post(
            '/image/upload/zip/1', data={'image': file},
            headers={'Authorization': 'Bearer %s' % access_token})
        assert '400 BAD REQUEST' == rv.status
