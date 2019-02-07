from instadam.utils.auth import verify_token


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
    rv = register(client, 'someone@illinois.edu', 'test0', 'password')
    code = rv.status
    json_data = rv.get_json()
    assert code == '201 CREATED'
    assert 'access_token' in json_data

    rv = login(client, 'test0', 'password')
    code = rv.status
    assert code == '201 CREATED'
    assert 'access_token' in json_data

    rv = login(client, 'test0', 'password ')
    code = rv.status
    assert code == '401 UNAUTHORIZED'
    json_data = rv.get_json()
    assert json_data is None

    rv = login(client, 'test1', 'password ')
    code = rv.status
    assert code == '401 UNAUTHORIZED'
    json_data = rv.get_json()
    assert json_data is None

    rv = client.post('/login', json={'password': '1235'}, follow_redirects=True)
    code = rv.status
    assert code == '400 BAD REQUEST'


def test_register(client):
    rv = register(client, 'someone1@illinois.edu', 'test1', 'password')
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

    rv = register(client, 'someone1@illinois.edu', 'test1', 'password')
    code = rv.status
    assert code == '401 UNAUTHORIZED'