from instadam.models.user import User


def test_user_repr(client):
    user = User(username='test_name', email='test@example.com')
    assert str(user) == '<User %r>' % 'test_name'


def test_verify_password(client):
    user = User(username='test_name', email='test@example.com')
    user.set_password('testasdfasdfasdf')
    assert not user.verify_password('asdf')
    assert user.verify_password('testasdfasdfasdf')
