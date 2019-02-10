from instadam.models.revoked_token import RevokedToken
from flask_jwt_extended import create_access_token

def test_token_repr(client):
    jti = 'jtitesttesttsettest'
    token = RevokedToken(jti=jti)
    assert token.__repr__() == jti