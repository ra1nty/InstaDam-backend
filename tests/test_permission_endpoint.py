"""Module related to testing all endpoint functionality with updating project
permissions
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

ADMIN_USERNAME = "test_admin"
ADMIN_PWD = "test_admin"
ANNOTATOR_USERNAME = "test_annotator"
ANNOTATOR_PWD = "test_annotator"


@pytest.fixture
def local_client():
    if os.path.isdir(Config.STATIC_STORAGE_DIR):
        shutil.rmtree(Config.STATIC_STORAGE_DIR)
    app = create_app(TEST_MODE)
    with app.app_context():
        db.reflect()
        db.drop_all()
        db.create_all()

        user = User(username=ADMIN_USERNAME, email='email@test_upload.com')
        user.set_password(ADMIN_PWD)
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

        user = User(username=ANNOTATOR_USERNAME, email='email2@test_upload.com')
        user.set_password(ANNOTATOR_PWD)

        db.session.add(user)
        db.session.flush()
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


def test_update_user_permission_readonly(local_client):
    access_token = successful_login(local_client, ADMIN_USERNAME, ADMIN_PWD)

    rv = local_client.put(
        '/project/1/permissions',
        json={
            'username': ANNOTATOR_USERNAME,
            'access_type': 'r',
        },
        headers={'Authorization': 'Bearer %s' % access_token})
    assert 200 == rv.status_code
    json_data = rv.get_json()
    assert 'msg' in json_data
    assert 'Permission added successfully' == json_data['msg']


def test_update_user_permission_duplicate_permission(local_client):
    access_token = successful_login(local_client, ADMIN_USERNAME, ADMIN_PWD)

    # Add READ_WRITE for the first time
    body = {
        'username': ANNOTATOR_USERNAME,
        'access_type': 'r',
    }
    rv = local_client.put(
        '/project/1/permissions',
        json=body,
        headers={'Authorization': 'Bearer %s' % access_token})
    assert 200 == rv.status_code
    json_data = rv.get_json()
    assert 'msg' in json_data
    assert 'Permission added successfully' == json_data['msg']

    # Add READ_WRITE for the second time
    body = {
        'username': ANNOTATOR_USERNAME,
        'access_type': 'r',
    }
    rv = local_client.put(
        '/project/1/permissions',
        json=body,
        headers={'Authorization': 'Bearer %s' % access_token})
    assert 200 == rv.status_code
    json_data = rv.get_json()
    assert 'msg' in json_data
    assert 'Permission already existed' == json_data['msg']


def test_update_user_permission_bad_access_type(local_client):
    access_token = successful_login(local_client, ADMIN_USERNAME, ADMIN_PWD)

    rv = local_client.put(
        '/project/1/permissions',
        json={
            'username': ANNOTATOR_USERNAME,
            'access_type': 'rwww',
        },
        headers={'Authorization': 'Bearer %s' % access_token})
    assert 400 == rv.status_code
    json_data = rv.get_json()
    assert 'msg' in json_data
    assert 'Not able to interpret access_type.' == json_data['msg']
