"""Module related to testing all endpoint functionality with the 
blueprint 'project/<project_id>/labels'
"""

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

        user = User(
            username='test_upload_user1',
            email='email@test_upload.com',
            privileges=PrivilegesEnum.ADMIN)
        user.set_password('TestTest1')
        db.session.add(user)
        db.session.commit()

        project = Project(project_name='test/test', created_by=user.id)
        db.session.add(project)
        db.session.commit()

        permission = ProjectPermission(access_type=AccessTypeEnum.READ_WRITE)
        user.project_permissions.append(permission)
        project.permissions.append(permission)

        user = User(
            username='test_upload_user2', email='email2@test_upload.com')
        user.set_password('TestTest1')
        permission = ProjectPermission(access_type=AccessTypeEnum.READ_WRITE)
        user.project_permissions.append(permission)
        project.permissions.append(permission)
        db.session.add(user)
        db.session.commit()

    client = app.test_client()
    yield client


def successful_login(client, username, password):
    rv = client.post(
        '/login',
        json={
            'username': username,
            'password': password
        },
        follow_redirects=True)

    assert '201 CREATED' == rv.status
    json_data = rv.get_json()
    assert 'access_token' in json_data

    return json_data['access_token']


test_data = [
    ({
        'label_text': 'my_label',
        'label_color': '#000000'
    }, '200 OK', 'label_id'),
    ({
        'label_color': '#000000'
    }, '400 BAD REQUEST', 'msg'),
    ({
        'label_text': 'my_label',
    }, '400 BAD REQUEST', 'msg'),
]


@pytest.mark.parametrize("json, status, in_json", test_data)
def test_add_label(json, status, in_json, local_client):
    access_token = successful_login(local_client, 'test_upload_user1',
                                    'TestTest1')
    rv = local_client.post(
        '/project/1/labels',
        json=json,
        headers={'Authorization': 'Bearer %s' % access_token})
    assert status == rv.status
    json_data = rv.get_json()
    assert in_json in json_data


test_data = [('my_label_1', '#001000', 'my_label_2', '#000111'),
             ('qwer', '#000000', 'asdf', '#333333')]


@pytest.mark.parametrize("label_text1, label_color1, label_text2, label_color2",
                         test_data)
def test_get_label(label_text1, label_color1, label_text2, label_color2,
                   local_client):
    access_token = successful_login(local_client, 'test_upload_user1',
                                    'TestTest1')
    rv = local_client.post(
        '/project/1/labels',
        json={
            'label_text': label_text1,
            'label_color': label_color1
        },
        headers={'Authorization': 'Bearer %s' % access_token})
    assert '200 OK' == rv.status
    json_data = rv.get_json()
    assert 'label_id' in json_data

    rv = local_client.post(
        '/project/1/labels',
        json={
            'label_text': label_text2,
            'label_color': label_color2
        },
        headers={'Authorization': 'Bearer %s' % access_token})
    assert '200 OK' == rv.status
    json_data = rv.get_json()
    assert 'label_id' in json_data

    rv = local_client.get(
        '/project/1/labels',
        headers={'Authorization': 'Bearer %s' % access_token})

    assert '200 OK' == rv.status
    json_data = rv.get_json()
    assert 'labels' in json_data
    labels = sorted(json_data['labels'], key=lambda label: label['label_id'])
    assert 2 == len(labels)

    assert label_text1 == labels[0]['text']
    assert label_text2 == labels[1]['text']
    assert label_color1 == labels[0]['color']
    assert label_color2 == labels[1]['color']
