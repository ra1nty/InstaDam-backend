from email.utils import parseaddr

from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import (create_access_token, get_raw_jwt, jwt_required)
from sqlalchemy.exc import IntegrityError

from .app import db, jwt
from .models.revoked_token import RevokedToken
from .models.user import User
from .utils import construct_msg

bp = Blueprint('auth', __name__, url_prefix='')


def credential_checking(password, email):
    """Check the validity of the given user credential.

    Raises:
        IntegrityError -- An error occurred when invalidate user credential is
        given
    """
    if len(password) < 8:
        abort(400, 'Password should be longer than 8 characters.')

    has_digit = any([c.isdigit() for c in password])
    if not has_digit:
        abort(400, 'Password must have at least one digit.')

    has_upper = any([c.isupper() for c in password])
    if not has_upper:
        abort(400, 'Password must have at least one uppercase letter.')

    # Check email
    if parseaddr(email) == ('', '') or '@' not in email:
        abort(400, 'Please enter a valid email address.')


@bp.route('/login', methods=['POST'])
def login():
    """User login endpoint for application

    Take POST data as json with userame and password.
    Return a json web token as access token.

    Usage:
        POST /login
    """
    req = request.get_json()
    if 'username' not in req or 'password' not in req:
        abort(400, 'Missing credentials')
    username = req['username']
    user = User.query.filter_by(username=req['username']).first()
    if user is not None:
        if user.verify_password(req['password']):
            return jsonify(
                {'access_token':
                 create_access_token(identity=user.username)}), 201
    abort(401, 'User %s not found or incorrect password' % username)


@bp.route('/register', methods=['POST'])
def register():
    """User register endpoint for application

    Take POST data as json with userame and password.
    Return a json web token as access token.

    Usage:
        POST /register
    """
    req = request.get_json()
    if 'username' not in req or 'password' not in req or 'email' not in req:
        abort(400, 'Missing credentials')

    username = req['username']
    password = req['password']
    email = req['email']

    credential_checking(password, email)

    user = User(username=username, email=email)
    user.set_password(password)
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(401, 'User/Email already exist')
    return jsonify(
        {'access_token': create_access_token(identity=user.username)}), 201


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    token = RevokedToken.query.filter_by(jti=jti).first()
    return token is not None


@bp.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    """User logout endpoint for application

    Invalidate the token in the request header

    Usage:
        DELETE /logout
    """
    jti = get_raw_jwt()['jti']
    token = RevokedToken(jti=jti)
    db.session.add(token)
    db.session.commit()
    return construct_msg('Logged out'), 200
