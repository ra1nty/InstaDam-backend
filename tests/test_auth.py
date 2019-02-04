def register(client, email, username, password):
    return client.post('/register', json={
        'email' : email,
        'username' : username,
        'password' : password
    }, follow_redirects=True)

def login(client, username, password):
    return client.post('/login', json={
        'username' : username,
        'password' : password
    }, follow_redirects=True)

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