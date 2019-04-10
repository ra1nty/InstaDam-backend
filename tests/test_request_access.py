import pytest

from instadam.app import create_app, db
from instadam.models.project import Project
from instadam.models.user import PrivilegesEnum, User
from tests.conftest import TEST_MODE

ADMIN_USERNAME = "test_admin"
ADMIN_PWD = "test_admin"
ANNOTATOR1_USERNAME = "test_annotator1"
ANNOTATOR1_EMAIL = "test_annotator1@test_upload.com"
ANNOTATOR2_USERNAME = "test_annotator2"
ANNOTATOR2_EMAIL = "test_annotator2@test_upload.com"
ANNOTATOR_PWD = "test_annotator"


@pytest.fixture
def local_client():
    app = create_app(TEST_MODE)
    with app.app_context():
        db.reflect()
        db.drop_all()
        db.create_all()

        user = User(username=ADMIN_USERNAME, email='email@test_upload.com',
                    privileges=PrivilegesEnum.ADMIN)
        user.set_password(ADMIN_PWD)
        db.session.add(user)
        db.session.flush()
        db.session.commit()

        project = Project(project_name='test/test1', created_by=user.id)
        db.session.add(project)
        db.session.flush()
        db.session.commit()

        project = Project(project_name='test/test2', created_by=user.id)
        db.session.add(project)
        db.session.flush()
        db.session.commit()

        # first annotator
        user = User(username=ANNOTATOR1_USERNAME,
                    email=ANNOTATOR1_EMAIL)
        user.set_password(ANNOTATOR_PWD)

        db.session.add(user)
        db.session.flush()
        db.session.commit()

        # second annotator
        user = User(username=ANNOTATOR2_USERNAME,
                    email=ANNOTATOR2_EMAIL)
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


def test_request_success_r(local_client):
    access_token = successful_login(
        local_client,
        ANNOTATOR1_USERNAME,
        ANNOTATOR_PWD
    )
    rv = local_client.post(
        '/project/1/request', json={
            'message_type': 'r_request'
        },
        headers={'Authorization': 'Bearer %s' % access_token}
    )

    assert 200 == rv.status_code
    json_data = rv.get_json()
    assert 'msg' in json_data
    assert 'Message sent successfully' == json_data['msg']


def test_request_success_rw(local_client):
    access_token = successful_login(
        local_client,
        ANNOTATOR1_USERNAME,
        ANNOTATOR_PWD
    )
    rv = local_client.post(
        '/project/1/request', json={
            'message_type': 'rw_request'
        },
        headers={'Authorization': 'Bearer %s' % access_token}
    )

    assert 200 == rv.status_code
    json_data = rv.get_json()
    assert 'msg' in json_data
    assert 'Message sent successfully' == json_data['msg']


def test_request_fail_unknown_key(local_client):
    access_token = successful_login(
        local_client,
        ANNOTATOR1_USERNAME,
        ANNOTATOR_PWD
    )
    rv = local_client.post(
        '/project/1/request', json={
            'message_type': 'unknown_key'
        },
        headers={'Authorization': 'Bearer %s' % access_token}
    )

    assert 400 == rv.status_code
    json_data = rv.get_json()
    assert 'msg' in json_data
    assert 'Not able to interpret message_type.' == json_data['msg']
