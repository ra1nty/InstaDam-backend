"""Module related to testing all endpoint functionality with changing 
privilege of user
"""

import pytest

from instadam.app import create_app, db
from instadam.models.user import PrivilegesEnum, User
from tests.conftest import TEST_MODE


@pytest.fixture
def local_client():
    app = create_app(TEST_MODE)
    with app.app_context():
        db.reflect()
        db.drop_all()
        db.create_all()

        admin = User(
            username='test_upload_admin1',
            email='email@test_load.com',
            privileges=PrivilegesEnum.ADMIN)
        admin.set_password('TestTest1')
        db.session.add(admin)
        db.session.commit()

        annotator = User(
            username='test_upload_annotator1',
            email='email2@test_load.com',
            privileges=PrivilegesEnum.ANNOTATOR)
        annotator.set_password('TestTest2')
        db.session.add(annotator)
        db.session.commit()

        annotator_2 = User(
            username='test_upload_annotator2', email='email3@test_load.com')
        annotator_2.set_password('TestTest3')
        db.session.add(annotator_2)
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
    ('test_upload_admin1', 'TestTest1', {
        'username': 'test_upload_annotator1',
        'privilege': 'admin'
    }, '200 OK'),
    ('test_upload_annotator1', 'TestTest2', {
        'username': 'test_upload_annotator2',
        'privilege': 'admin'
    }, '401 UNAUTHORIZED'),
    ('test_upload_admin1', 'TestTest1', {
        'username': 'test_upload_annotator1'
    }, '400 BAD REQUEST'),
    ('test_upload_admin1', 'TestTest1', None, '400 BAD REQUEST'),
]


@pytest.mark.parametrize("requester, requester_pass, json, expected", test_data)
def test_change_privilege(requester, requester_pass, json, expected,
                          local_client):
    token = successful_login(local_client, requester, requester_pass)
    response = local_client.put(
        '/user/privilege/',
        json=json,
        headers={'Authorization': 'Bearer %s' % token})
    assert expected == response.status


def test_change_info_success(local_client):
    token = successful_login(local_client, 'test_upload_annotator2',
                             'TestTest3')
    response = local_client.put(
        '/user/',
        json={'username': 'lololol11', 'current_password': 'TestTest3'},
        headers={'Authorization': 'Bearer %s' % token})

    assert '200 OK' == response.status

    successful_login(local_client, 'lololol11', 'TestTest3')


def test_change_info_auth_fail(local_client):
    token = successful_login(local_client, 'test_upload_annotator2',
                             'TestTest3')
    response = local_client.put(
        '/user/',
        json={'username': 'lololol11', 'current_password': '1234'},
        headers={'Authorization': 'Bearer %s' % token})

    assert '401 UNAUTHORIZED' == response.status


def test_change_info_auth_fail2(local_client):
    token = successful_login(local_client, 'test_upload_annotator2',
                             'TestTest3')
    response = local_client.put(
        '/user/',
        json={'username': 'test_upload_admin1',
              'current_password': 'TestTest3'},
        headers={'Authorization': 'Bearer %s' % token})

    assert '400 BAD REQUEST' == response.status


def test_change_info_auth_fail3(local_client):
    token = successful_login(local_client, 'test_upload_annotator2',
                             'TestTest3')
    response = local_client.put(
        '/user/',
        json={'username': 'test_upload_admin1', 'email': 'test.illinois.edu',
              'current_password': 'TestTest3'},
        headers={'Authorization': 'Bearer %s' % token})

    assert '400 BAD REQUEST' == response.status
