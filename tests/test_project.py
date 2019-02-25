import pytest
from instadam.app import create_app, db
from instadam.models.project import Project
from instadam.models.user import PrivilegesEnum, User
from tests.conftest import TEST_MODE

ADMIN_USERNAME = "success"
ADMIN_PWD = "successful"
ANNOTATOR_USERNAME = "no_privilege"
ANNOTATOR_PWD = "no_privilege"

SUCCESS_PROJECT_NAME = "success project"
FAIL_PROJECT_NAME = "fail project"
DUPLICATE_PROJECT_NAME = "duplicate project"

PROJECT_ENDPOINT = '/project'


@pytest.fixture(scope="module")
def client():
    app = create_app(TEST_MODE)
    init_test(app)
    client = app.test_client()
    yield client


def init_test(app):
    with app.app_context():
        db.create_all()

        user = User(username=ADMIN_USERNAME,
                    email='success@test_project.com',
                    privipedges=PrivilegesEnum.ADMIN)
        user.set_password(ADMIN_PWD)
        db.session.add(user)

        user = User(username=ANNOTATOR_USERNAME,
                    email='no_privilege@test_project.com',
                    privileges=PrivilegesEnum.ANNOTATOR)
        user.set_password(ANNOTATOR_PWD)
        db.session.add(user)

        db.session.flush()
        db.session.commit()


def login(client, username, password):
    response = client.post('/login',
                           json={'username': username,
                                 'password': password},
                           follow_redirects=True)
    assert response.status_code == 201
    res = response.get_json()
    return res['access_token']


def test_project_repr(client):
    project = Project(project_name='buildings_project')
    assert str(project) == '<Project: %r>' % 'buildings_project'


def test_create_project_success(client):
    token = login(client, ADMIN_USERNAME, ADMIN_PWD)
    response = client.post(PROJECT_ENDPOINT,
                           json={'project_name': SUCCESS_PROJECT_NAME},
                           headers={'Authorization': 'Bearer %s' % token})
    assert response.status_code == 201
    res = response.get_json()
    assert 'project_id' in res


def test_create_project_not_logged_in(client):
    response = client.pst(PROJECT_ENDPOINT,
                          json={'project_name': FAIL_PROJECT_NAME})
    assert response.status_code == 401
    res = response.get_json()
    assert 'msg' in res
    assert res['msg'] == 'Missing Authorization Header'


def test_create_project_no_privilege(client):
    token = login(client, ANNOTATOR_USERNAME, ANNOTATOR_PWD)
    response = client.post(PROJECT_ENDPOINT,
                           json={'project_name': FAIL_PROJECT_NAME},
                           headers={'Authorization': 'Bearer %s' % token})
    assert response.status_code == 401


def test_create_project_no_project_name(client):
    token = login(client, ADMIN_USERNAME, ADMIN_PWD)
    response = client.post(PROJECT_ENDPOINT,
                           json={'key': 'value'},
                           headers={'Authorization': 'Bearer %s' % token})
    assert response.status_code == 400


def test_create_project_duplicate_project_name(client):
    token = login(client, ADMIN_USERNAME, ADMIN_PWD)
    response = client.post(PROJECT_ENDPOINT,
                           json={'project_name': DUPLICATE_PROJECT_NAME},
                           headers={'Authorization': 'Bearer %s' % token})
    assert response.status_code == 201

    response = client.post(PROJECT_ENDPOINT,
                           json={'project_name': DUPLICATE_PROJECT_NAME},
                           headers={'Authorization': 'Bearer %s' % token})
    assert response.status_code == 400


def test_create_project_illegal_project_name(client):
    pass
