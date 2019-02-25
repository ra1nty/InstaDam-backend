import filecmp
import os
import shutil

import pytest
from werkzeug.datastructures import FileStorage

from instadam.app import create_app, db
from instadam.config import Config
from instadam.models.image import Image
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

        admin = User(
            username='test_upload_admin1',
            email='email@test_upload.com',
            privileges=PrivilegesEnum.ADMIN)
        admin.set_password('TestTest1')
        db.session.add(admin)
        db.session.flush()
        db.session.commit()

        annotator = User(
            username='test_upload_annotator1', email='email2@test_upload.com')
        annotator.set_password('TestTest2')
        permission = ProjectPermission(access_type=AccessTypeEnum.READ_WRITE)
        annotator.project_permissions.append(permission)
        db.session.add(annotator)
        db.session.flush()
        db.session.commit()

        project = Project(project_name='TestProject', created_by=admin.id)
        db.session.add(project)
        db.session.flush()
        db.session.commit()

        permission = ProjectPermission(access_type=AccessTypeEnum.READ_WRITE)
        annotator.project_permissions.append(permission)
        project.permissions.append(permission)

        test_image = Image(
            image_name='cat.jpg',
            image_path='test_dir/test_dir_2/cat.jpg',
            project_id=project.id)
        db.session.add(test_image)
        db.session.flush()
        db.session.commit()

        test_image_2 = Image(
            image_name='dog.png',
            image_path='test_dir/test_dir_2/dog.png',
            project_id=project.id)
        db.session.add(test_image_2)
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


def test_load_unannotated_images(local_client):
    access_token = successful_login(local_client, 'test_upload_annotator1',
                                    'TestTest2')

    res = local_client.get(
        '/project/new', headers={'Authorization': 'Bearer %s' % access_token})

    json_res = res.get_json()
    assert len(res['unannotated_images']) == 2

    assert json_res['unannotated_images'][0][
        'image_name'] == 'cat.jpg' or json_res['unannotated_images'][1][
            'image_name'] == 'cat.jpg'
    assert json_res['unannotated_images'][0][
        'image_name'] == 'dog.png' or json_res['unannotated_images'][1][
            'image_name'] == 'dog.png'

    assert json_res['unannotated_images'][0][
        'image_path'] == 'test_dir/test_dir_2/cat.jpg' or json_res[
            'unannotated_images'][1][
                'image_path'] == 'test_dir/test_dir_2/cat.jpg'
    assert json_res['unannotated_images'][0][
        'image_path'] == 'test_dir/test_dir_2/dog.png' or json_res[
            'unannotated_images'][1][
                'image_path'] == 'test_dir/test_dir_2/dog.png'


def test_load_project_images(local_client):
    access_token = successful_login(local_client, 'test_upload_annotator1',
                                    'TestTest2')

    res = local_client.get(
        '/project/1/images',
        headers={'Authorization': 'Bearer %s' % access_token})

    json_res = res.get_json()
    assert len(json_res['project_images']) == 2

    assert json_res['unannotated_images'][0][
        'image_name'] == 'cat.jpg' or json_res['unannotated_images'][1][
            'image_name'] == 'cat.jpg'
    assert json_res['unannotated_images'][0][
        'image_name'] == 'dog.png' or json_res['unannotated_images'][1][
            'image_name'] == 'dog.png'

    assert json_res['unannotated_images'][0][
        'image_path'] == 'test_dir/test_dir_2/cat.jpg' or json_res[
            'unannotated_images'][1][
                'image_path'] == 'test_dir/test_dir_2/cat.jpg'
    assert json_res['unannotated_images'][0][
        'image_path'] == 'test_dir/test_dir_2/dog.png' or json_res[
            'unannotated_images'][1][
                'image_path'] == 'test_dir/test_dir_2/dog.png'


def test_load_image(local_client):
    access_token = successful_login(local_client, 'test_upload_annotator1',
                                    'TestTest2')

    res = local_client.get(
        '/project/1/image/1',
        headers={'Authorization': 'Bearer %s' % access_token})

    json_res = res.get_json()
    assert id in json_res
    assert json_res['path'] == 'test_dir/test_dir_2/cat.jpg'


def test_load_image_fail(local_client):
    access_token = successful_login(local_client, 'test_upload_annotator1',
                                    'TestTest2')

    res = local_client.get(
        '/project/1/image/5',
        headers={'Authorization': 'Bearer %s' % access_token})

    assert '404 NOT FOUND' == res.status
