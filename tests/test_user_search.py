"""Module related to testing all endpoint functionality with searching users
"""

import pytest

from instadam.app import create_app, db
from instadam.config import Config
from instadam.models.user import PrivilegesEnum, User
from tests.conftest import TEST_MODE


@pytest.fixture
def local_client():
    app = create_app(TEST_MODE)
    with app.app_context():
        db.reflect()
        db.drop_all()
        db.create_all()

        user_1 = User(
            username='user_1',
            email='email_1@test_upload.com',
            privileges=PrivilegesEnum.ADMIN)
        user_1.set_password('TestTest1')

        user_2 = User(
            username='user_2',
            email='email_2@test_upload.com',
            privileges=PrivilegesEnum.ANNOTATOR)
        user_2.set_password('TestTest2')

        user_3 = User(
            username='drifter',
            email='drifting@gmail.com',
            privileges=PrivilegesEnum.ANNOTATOR)
        user_3.set_password('TestTest3')

        user_4 = User(
            username='jordanne',
            email='jordanne@caterpillar.com',
            privileges=PrivilegesEnum.ADMIN)
        user_4.set_password('TestTest4')

        db.session.add(user_1)
        db.session.add(user_2)
        db.session.add(user_3)
        db.session.add(user_4)
        db.session.flush()
        db.session.commit()

    client = app.test_client()
    yield client


def successful_login(client, username, password):
    response = client.post(
        '/login',
        json={
            'username': username,
            'password': password
        },
        follow_redirects=True)
    assert response.status_code == 201
    res = response.get_json()
    return res['access_token']


def test_search_users_by_username(local_client):
    access_token = successful_login(local_client, 'user_1', 'TestTest1')

    res = local_client.get(
        '/users/search?q=drifter',
        headers={'Authorization': 'Bearer %s' % access_token})

    json_res = res.get_json()
    assert len(json_res['users']) == 1

    assert json_res['users'][0]['username'] == 'drifter'
    assert json_res['users'][0]['email'] == 'drifting@gmail.com'


def test_search_users_by_email(local_client):
    access_token = successful_login(local_client, 'user_1', 'TestTest1')

    res = local_client.get(
        '/users/search?q=jordanne@caterpillar',
        headers={'Authorization': 'Bearer %s' % access_token})

    json_res = res.get_json()
    assert len(json_res['users']) == 1

    assert json_res['users'][0]['username'] == 'jordanne'
    assert json_res['users'][0]['email'] == 'jordanne@caterpillar.com'


def test_search_users_permission_fail(local_client):
    access_token = successful_login(local_client, 'user_2', 'TestTest2')

    res = local_client.get(
        '/users/search?q=jordanne',
        headers={'Authorization': 'Bearer %s' % access_token})

    assert '401 UNAUTHORIZED' == res.status


def test_search_users_no_users(local_client):
    access_token = successful_login(local_client, 'user_1', 'TestTest1')

    res = local_client.get(
        '/users/search?q=jordank',
        headers={'Authorization': 'Bearer %s' % access_token})

    json_res = res.get_json()
    assert len(json_res['users']) == 0


def test_search_user_partial_match(local_client):
    access_token = successful_login(local_client, 'user_1', 'TestTest1')

    res = local_client.get(
        '/users/search?q=jordan',
        headers={'Authorization': 'Bearer %s' % access_token})

    json_res = res.get_json()
    assert len(json_res['users']) == 1

    assert json_res['users'][0]['username'] == 'jordanne'
    assert json_res['users'][0]['email'] == 'jordanne@caterpillar.com'