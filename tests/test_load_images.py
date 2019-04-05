import base64
import os
import shutil
from io import BytesIO

import pytest
from PIL import Image as PILImage

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

        rw_permission = ProjectPermission(access_type=AccessTypeEnum.READ_WRITE)
        r_permission = ProjectPermission(access_type=AccessTypeEnum.READ_ONLY)

        admin = User(
            username='test_upload_admin1',
            email='email@test_load.com',
            privileges=PrivilegesEnum.ADMIN)
        admin.set_password('TestTest1')
        admin.project_permissions.append(rw_permission)
        db.session.add(admin)
        db.session.flush()
        db.session.commit()

        annotator = User(
            username='test_upload_annotator1',
            email='email2@test_load.com',
            privileges=PrivilegesEnum.ANNOTATOR)
        annotator.set_password('TestTest2')
        annotator.project_permissions.append(r_permission)
        db.session.add(annotator)
        db.session.flush()
        db.session.commit()

        annotator_2 = User(
            username='test_upload_annotator2', email='email3@test_load.com')
        annotator_2.set_password('TestTest3')
        db.session.add(annotator_2)
        db.session.flush()
        db.session.commit()

        project = Project(project_name='TestProject', created_by=admin.id)
        db.session.add(project)
        db.session.flush()
        db.session.commit()

        project.permissions.append(rw_permission)
        project.permissions.append(r_permission)

        test_image = Image(
            image_name='cat.jpg',
            image_url='test_dir/test_dir_2/cat.jpg',
            project_id=project.id)
        db.session.add(test_image)
        db.session.flush()
        db.session.commit()

        test_image_2 = Image(
            image_name='dog.png',
            image_url='test_dir/test_dir_2/dog.png',
            project_id=project.id)
        db.session.add(test_image_2)
        db.session.flush()
        db.session.commit()

        test_image_3 = Image(
            image_name='cat.jpg',
            image_url='tests/cat.jpg',
            image_storage_path='tests/cat.jpg',
            project_id=project.id)
        db.session.add(test_image_3)
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
        '/projects/1/unannotated',
        headers={'Authorization': 'Bearer %s' % access_token})

    json_res = res.get_json()
    assert len(json_res['unannotated_images']) == 3

    assert json_res['unannotated_images'][0]['name'] == 'cat.jpg' or json_res[
        'unannotated_images'][1]['name'] == 'cat.jpg'
    assert json_res['unannotated_images'][0]['name'] == 'dog.png' or json_res[
        'unannotated_images'][1]['name'] == 'dog.png'

    assert json_res['unannotated_images'][0][
        'path'] == 'test_dir/test_dir_2/cat.jpg' or json_res[
            'unannotated_images'][1]['path'] == 'test_dir/test_dir_2/cat.jpg'
    assert json_res['unannotated_images'][0][
        'path'] == 'test_dir/test_dir_2/dog.png' or json_res[
            'unannotated_images'][1]['path'] == 'test_dir/test_dir_2/dog.png'


def test_load_unannotated_images_fail(local_client):
    access_token = successful_login(local_client, 'test_upload_annotator2',
                                    'TestTest3')

    res = local_client.get(
        '/projects/1/unannotated',
        headers={'Authorization': 'Bearer %s' % access_token})

    assert '401 UNAUTHORIZED' == res.status


def test_load_unannotated_images_fail_2(local_client):
    access_token = successful_login(local_client, 'test_upload_annotator1',
                                    'TestTest2')

    res = local_client.get(
        '/projects/3/unannotated',
        headers={'Authorization': 'Bearer %s' % access_token})

    assert '404 NOT FOUND' == res.status


def test_load_project_images(local_client):
    access_token = successful_login(local_client, 'test_upload_annotator1',
                                    'TestTest2')

    res = local_client.get(
        '/projects/1/images',
        headers={'Authorization': 'Bearer %s' % access_token})

    json_res = res.get_json()
    assert len(json_res['project_images']) == 3

    assert json_res['project_images'][0]['name'] == 'cat.jpg' or json_res[
        'project_images'][1]['name'] == 'cat.jpg'
    assert json_res['project_images'][0]['name'] == 'dog.png' or json_res[
        'project_images'][1]['name'] == 'dog.png'

    assert json_res['project_images'][0][
               'path'] == 'test_dir/test_dir_2/cat.jpg' or \
           json_res['project_images'][
               1]['path'] == 'test_dir/test_dir_2/cat.jpg'
    assert json_res['project_images'][0][
               'path'] == 'test_dir/test_dir_2/dog.png' or \
           json_res['project_images'][
               1]['path'] == 'test_dir/test_dir_2/dog.png'


def test_load_project_images_fail(local_client):
    access_token = successful_login(local_client, 'test_upload_annotator1',
                                    'TestTest2')

    res = local_client.get(
        '/projects/3/images',
        headers={'Authorization': 'Bearer %s' % access_token})

    assert '404 NOT FOUND' == res.status


def test_load_project_images_fail_2(local_client):
    access_token = successful_login(local_client, 'test_upload_annotator2',
                                    'TestTest3')

    res = local_client.get(
        '/projects/1/images',
        headers={'Authorization': 'Bearer %s' % access_token})

    assert '401 UNAUTHORIZED' == res.status


def test_load_image(local_client):
    access_token = successful_login(local_client, 'test_upload_annotator1',
                                    'TestTest2')

    res = local_client.get(
        '/image/1', headers={'Authorization': 'Bearer %s' % access_token})

    json_res = res.get_json()
    assert 'id' in json_res
    assert json_res['path'] == 'test_dir/test_dir_2/cat.jpg'


def test_load_image_fail(local_client):
    access_token = successful_login(local_client, 'test_upload_annotator1',
                                    'TestTest2')

    res = local_client.get(
        '/image/5', headers={'Authorization': 'Bearer %s' % access_token})

    assert '404 NOT FOUND' == res.status


def test_get_thumbnail(local_client):
    access_token = successful_login(local_client, 'test_upload_annotator1',
                                    'TestTest2')
    res = local_client.get(
        '/image/3/thumbnail?size_h=16&size_w=15',
        headers={'Authorization': 'Bearer %s' % access_token})
    json = res.get_json()
    assert '200 OK' == res.status
    assert 'image_id' in json
    assert 3 == json['image_id']
    assert 'png' == json['format']
    base64_str = json['base64_image']
    rep_img = PILImage.open(BytesIO(base64.b64decode(base64_str)))
    img = PILImage.open('tests/cat.jpg')
    img.thumbnail((16, 15), PILImage.ANTIALIAS)
    assert img.size == rep_img.size
