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
        db.session.flush()
        db.session.commit()

        annotator = User(
            username='test_upload_annotator1',
            email='email2@test_load.com',
            privileges=PrivilegesEnum.ANNOTATOR)
        annotator.set_password('TestTest2')
        db.session.add(annotator)
        db.session.flush()
        db.session.commit()

        annotator_2 = User(
            username='test_upload_annotator2', email='email3@test_load.com')
        annotator_2.set_password('TestTest3')
        db.session.add(annotator_2)
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


def test_change_user_privilege_success(local_client):
    token = successful_login(local_client, 'test_upload_admin1', 'TestTest1')
    response = local_client.put('/user/privilege/',
                                json={'username': 'test_upload_annotator1',
                                      'privilege': 'admin'},
                                headers={'Authorization': 'Bearer %s' % token})
    assert '200 OK' == response.status


def test_change_user_privilege_fail1(local_client):
    token = successful_login(local_client, 'test_upload_annotator1',
                             'TestTest2')
    response = local_client.put('/user/privilege/',
                                json={'username': 'test_upload_annotator2',
                                      'privilege': 'admin'},
                                headers={'Authorization': 'Bearer %s' % token})
    assert '403 FORBIDDEN' == response.status


def test_change_user_privilege_fail2(local_client):
    token = successful_login(local_client, 'test_upload_admin1', 'TestTest1')
    response = local_client.put('/user/privilege/',
                                json={'privilege': 'admin'},
                                headers={'Authorization': 'Bearer %s' % token})
    assert '400 BAD REQUEST' == response.status


def test_change_user_privilege_fail3(local_client):
    token = successful_login(local_client, 'test_upload_admin1', 'TestTest1')
    response = local_client.put('/user/privilege/',
                                headers={'Authorization': 'Bearer %s' % token})
    assert '400 BAD REQUEST' == response.status
