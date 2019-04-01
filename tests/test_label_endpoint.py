import os
import shutil

import pytest

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
        db.reflect()
        db.drop_all()
        db.create_all()

        user = User(username='test_upload_user1', email='email@test_upload.com',
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

        user = User(username='test_upload_user2',
                    email='email2@test_upload.com')
        user.set_password('TestTest1')
        permission = ProjectPermission(access_type=AccessTypeEnum.READ_WRITE)
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


def test_add_label(local_client):
    access_token = successful_login(local_client, 'test_upload_user1',
                                    'TestTest1')
    rv = local_client.post(
        '/project/1/labels', json={'label_name': 'my_label', 'label_color': '#000000'},
        headers={'Authorization': 'Bearer %s' % access_token})
    assert '200 OK' == rv.status
    json_data = rv.get_json()
    assert 'msg' in json_data
    assert 'Label added successfully' == json_data['msg']


def test_get_label(local_client):
    access_token = successful_login(local_client, 'test_upload_user1',
                                    'TestTest1')
    rv = local_client.post(
        '/project/1/labels', json={'label_name': 'my_label_1', 'label_color': '#000000'},
        headers={'Authorization': 'Bearer %s' % access_token})
    assert '200 OK' == rv.status
    json_data = rv.get_json()
    assert 'msg' in json_data
    assert 'Label added successfully' == json_data['msg']

    rv = local_client.post(
        '/project/1/labels', json={'label_name': 'my_label_2', 'label_color': '#000000'},
        headers={'Authorization': 'Bearer %s' % access_token})
    assert '200 OK' == rv.status
    json_data = rv.get_json()
    assert 'msg' in json_data
    assert 'Label added successfully' == json_data['msg']

    rv = local_client.get(
        '/project/1/labels',
        headers={'Authorization': 'Bearer %s' % access_token})

    assert '200 OK' == rv.status
    json_data = rv.get_json()
    assert 'labels' in json_data
    labels = json_data['labels']
    assert 3 == len(labels)

    for label in labels:
        label_id = label['id']
        assert 'my_label_%d' % label_id == label['name']
