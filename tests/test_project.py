import pytest

from instadam.app import create_app, db
from instadam.models.project import Project
from instadam.models.project_permission import AccessTypeEnum, ProjectPermission
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
LIST_PROJECT_ENDPOINT = '/projects'


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
                    privileges=PrivilegesEnum.ADMIN)
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
    response = client.post(PROJECT_ENDPOINT,
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


@pytest.fixture
def get_project_fixture():
    app = create_app(TEST_MODE)
    with app.app_context():
        db.reflect()
        db.drop_all()
        db.create_all()

        user = User(username=ADMIN_USERNAME,
                    email='success@test_project.com',
                    privileges=PrivilegesEnum.ADMIN)
        user.set_password(ADMIN_PWD)
        db.session.add(user)

        db.session.flush()
        db.session.commit()

        project = Project(project_name='test1', created_by=user.id)
        db.session.add(project)
        db.session.flush()
        db.session.commit()

        permission = ProjectPermission(access_type=AccessTypeEnum.READ_WRITE)
        user.project_permissions.append(permission)
        project.permissions.append(permission)

        user = User(username=ANNOTATOR_USERNAME,
                    email='no_privilege@test_project.com',
                    privileges=PrivilegesEnum.ANNOTATOR)
        user.set_password(ANNOTATOR_PWD)

        db.session.add(user)
        db.session.flush()
        db.session.commit()

        permission = ProjectPermission(access_type=AccessTypeEnum.READ_ONLY)
        user.project_permissions.append(permission)
        project.permissions.append(permission)

        db.session.flush()
        db.session.commit()

    client = app.test_client()
    yield client


def test_list_projects(get_project_fixture):
    token = login(get_project_fixture, ANNOTATOR_USERNAME, ANNOTATOR_PWD)
    response = get_project_fixture.get(
        LIST_PROJECT_ENDPOINT,
        headers={'Authorization': 'Bearer %s' % token})
    assert response.status_code == 200
    json = response.get_json()
    assert 1 == len(json)
    assert 'test1' == json[0]['name']
    assert not json[0]['is_admin']

    token = login(get_project_fixture, ADMIN_USERNAME, ADMIN_PWD)
    response = get_project_fixture.get(
        LIST_PROJECT_ENDPOINT,
        headers={'Authorization': 'Bearer %s' % token})
    assert response.status_code == 200
    json = response.get_json()
    assert 1 == len(json)
    assert 'test1' == json[0]['name']
    assert json[0]['is_admin']
    assert 1 == json[0]['id']


def test_list_project_users(get_project_fixture):
    token = login(get_project_fixture, ADMIN_USERNAME, ADMIN_PWD)
    project_id = 1
    response = get_project_fixture.get(
        '/project/%d/users' % project_id,
        headers={'Authorization': 'Bearer %s' % token})
    assert response.status_code == 200
    json = response.get_json()
    assert len(json) == 2
    assert 'access_type' in json[0]
    assert 'user' in json[0]
    assert 'username' in json[0]['user']
    assert 'email' in json[0]['user']
    assert 'created_at' in json[0]['user']
    assert 'privileges' in json[0]['user']
