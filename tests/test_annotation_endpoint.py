"""Module related to testing all endpoint functionality with the 
blueprint '/annotation/...'
"""

import base64
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
        db.reflect()
        db.drop_all()
        db.create_all()

        user = User(
            username='test_upload_user1',
            email='email@test_upload.com',
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

        user = User(
            username='test_upload_user2', email='email2@test_upload.com')
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
        json={
            'username': username,
            'password': password
        },
        follow_redirects=True)

    assert '201 CREATED' == rv.status
    json_data = rv.get_json()
    assert 'access_token' in json_data

    return json_data['access_token']


@pytest.fixture
def image_label_uploaded(local_client):
    access_token = successful_login(local_client, 'test_upload_user1',
                                    'TestTest1')
    with open('tests/cat.jpg', 'rb') as img:
        file = FileStorage(img)
        rv = local_client.post(
            '/image/upload/1',
            data={'image': file},
            headers={'Authorization': 'Bearer %s' % access_token})
        assert '200 OK' == rv.status
        json_data = rv.get_json()
        assert 'msg' in json_data
        assert 'Image added successfully' == json_data['msg']

    rv = local_client.post(
        '/project/1/labels',
        json={
            'label_text': 'my_label',
            'label_color': '#000000'
        },
        headers={'Authorization': 'Bearer %s' % access_token})
    assert '200 OK' == rv.status
    json_data = rv.get_json()
    assert 'label_id' in json_data
    yield local_client


def test_add_and_get_annotation(image_label_uploaded):
    access_token = successful_login(image_label_uploaded, 'test_upload_user1',
                                    'TestTest1')

    rv = image_label_uploaded.get(
        '/projects/1/images',
        headers={'Authorization': 'Bearer %s' % access_token})

    json = rv.get_json()
    assert 1 == len(json['project_images'])
    assert not json['project_images'][0]['is_annotated']

    with open('tests/cat.jpg', 'rb') as img:
        base64_str = base64.b64encode(img.read()).decode('utf-8')
        labels = [{
            'label_id': 1,
            'bitmap': base64_str,
            'vector': {
                'name': 'test',
                'user': 'admin'
            }
        }]
        rv = image_label_uploaded.post(
            '/annotation/',
            json={
                'project_id': 1,
                'label_id': 1,
                'image_id': 1,
                'labels': labels
            },
            headers={'Authorization': 'Bearer %s' % access_token})
        assert '200 OK' == rv.status
        json_data = rv.get_json()
        assert 'msg' in json_data
        print(json_data['msg'])
        assert 'Annotation saved successfully' == json_data['msg']

        rv = image_label_uploaded.get(
            '/projects/1/images',
            headers={'Authorization': 'Bearer %s' % access_token})

        json = rv.get_json()
        assert 1 == len(json['project_images'])
        assert json['project_images'][0]['is_annotated']

        rv = image_label_uploaded.get(
            '/annotation/1/',
            headers={'Authorization': 'Bearer %s' % access_token})

        assert '200 OK' == rv.status
        json_data = rv.get_json()
        assert len(json_data) == 1
        assert 'bitmap' in json_data[0]
        assert base64_str == json_data[0]['bitmap']
        vector = json_data[0]['vector']
        assert 'name' in vector
        assert 'test' == vector['name']
        assert 'user' in vector
        assert 'admin' == vector['user']

        labels[0]['vector']['test-test'] = 100
        rv = image_label_uploaded.post(
            '/annotation/',
            json={
                'project_id': 1,
                'label_id': 1,
                'image_id': 1,
                'labels': labels
            },
            headers={'Authorization': 'Bearer %s' % access_token})
        assert '200 OK' == rv.status
        json_data = rv.get_json()
        assert 'msg' in json_data
        print(json_data['msg'])
        assert 'Annotation saved successfully' == json_data['msg']

        rv = image_label_uploaded.get(
            '/annotation/1/',
            json={
                'project_id': 1,
                'label_id': 1,
                'image_id': 1
            },
            headers={'Authorization': 'Bearer %s' % access_token})

        assert '200 OK' == rv.status
        json_data = rv.get_json()
        assert len(json_data) == 1
        assert 'bitmap' in json_data[0]
        assert base64_str == json_data[0]['bitmap']
        vector = json_data[0]['vector']
        assert 'name' in vector
        assert 'test' == vector['name']
        assert 'user' in vector
        assert 'admin' == vector['user']
        assert 'test-test' in vector
        assert 100 == vector['test-test']
