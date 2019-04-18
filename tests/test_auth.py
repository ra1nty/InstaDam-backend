"""Module related to testing authentication (login, signup) 
functionality
"""
import pytest


def register(client, email, username, password):
    return client.post(
        '/register',
        json={
            'email': email,
            'username': username,
            'password': password
        },
        follow_redirects=True)


def login(client, username, password):
    return client.post(
        '/login',
        json={
            'username': username,
            'password': password
        },
        follow_redirects=True)


def test_auth(client):
    """Make sure login works."""
    rv = register(client, 'someone@illinois.edu', 'test0', 'Password0')
    code = rv.status
    json_data = rv.get_json()
    assert code == '201 CREATED'
    assert 'access_token' in json_data

    rv = login(client, 'test0', 'Password0')
    code = rv.status
    assert code == '201 CREATED'
    assert 'access_token' in json_data

    rv = login(client, 'test0', 'Password0 ')
    code = rv.status
    assert code == '401 UNAUTHORIZED'

    rv = login(client, 'test1', 'password ')
    code = rv.status
    assert code == '401 UNAUTHORIZED'

    rv = client.post('/login', json={'password': '1235'}, follow_redirects=True)
    code = rv.status
    assert code == '400 BAD REQUEST'


def test_register(client):
    rv = register(client, 'someone1@illinois.edu', 'test1', 'Password0')
    code = rv.status
    json_data = rv.get_json()
    assert code == '201 CREATED'
    assert 'access_token' in json_data

    rv = client.post(
        '/register',
        json={
            'username': 'asdf',
            'password': 'password'
        },
        follow_redirects=True)
    code = rv.status
    assert code == '400 BAD REQUEST'

    rv = register(client, 'someone1@illinois.edu', 'test1', 'Password0')
    code = rv.status
    assert code == '401 UNAUTHORIZED'


def test_logout(client):
    rv = register(client, 'someone2@illinois.edu', 'test2', 'Password0')
    code = rv.status
    json_data = rv.get_json()
    assert code == '201 CREATED'
    assert 'access_token' in json_data
    access_token = json_data['access_token']

    rv = login(client, 'test2', 'Password0')
    code = rv.status
    assert code == '201 CREATED'
    assert 'access_token' in json_data

    rv = client.delete(
        '/logout',
        follow_redirects=True,
        headers={'Authorization': 'Bearer %s' % access_token})
    json_data = rv.get_json()
    code = rv.status
    assert code == '200 OK'
    assert 'msg' in json_data
    assert 'Logged out' == json_data['msg']

    # Try logout again should fail
    rv = client.delete(
        '/logout',
        follow_redirects=True,
        headers={'Authorization': 'Bearer %s' % access_token})
    json_data = rv.get_json()
    code = rv.status
    assert code == '401 UNAUTHORIZED'


test_data = [
    ('someone3@illinois.edu', 'test3', 'Password0', '201 CREATED',
     'access_token'),
    ('someone4@illinois.edu', 'test4', 'password', '400 BAD REQUEST', 'msg'),
    ('someone4@illinois.edu', 'test4', 'pass', '400 BAD REQUEST', 'msg'),
    ('someone4@illinois.edu', 'test4', 'password0', '400 BAD REQUEST', 'msg'),
    ('someone4#illinois.edu', 'test4', 'Password0', '400 BAD REQUEST', 'msg'),
]


@pytest.mark.parametrize("email, username, password, status, in_json",
                         test_data)
def test_credential_validation(email, username, password, status, in_json,
                               client):
    rv = register(client, email, username, password)
    code = rv.status
    json_data = rv.get_json()
    assert code == status
    assert in_json in json_data
