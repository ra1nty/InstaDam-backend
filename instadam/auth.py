from email.utils import parseaddr

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_raw_jwt, jwt_required)
from sqlalchemy.exc import IntegrityError

from .app import db, jwt
from .models.revoked_token import RevokedToken
from .models.user import User
from .utils import construct_msg
from .utils.exception import MsgException

bp = Blueprint('auth', __name__, url_prefix='')


def credential_checking(password, email):
    """Check the validity of the given user credential.

    * Needs a refactoring

    Raises:
        IntegrityError: An error occurred when invalidate user credential is given
    """
    if len(password) < 8:
        raise MsgException('Password should be longer than 8 characters.')
    has_digit = any([c.isdigit() for c in password])
    if not has_digit:
        raise MsgException('Password must have at least one digit.')
    has_upper = any([c.isupper() for c in password])
    if not has_upper:
        raise MsgException('Password must have at least one uppercase letter.')

    # Check email
    if parseaddr(email) == ('', '') or '@' not in email:
        raise MsgException('Please enter a valid email addresss.')


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
        return jsonify({'msg': 'Missing credentials'}), 400
    username = req['username']
    user = User.query.filter_by(username=req['username']).first()
    if user is not None:
        if user.verify_password(req['password']):
            return jsonify(
                {'access_token':
                 create_access_token(identity=user.username)}), 201
    return construct_msg('User %s not found' % username), 401


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
        return jsonify({'msg': 'Missing credentials'}), 400

    username = req['username']
    password = req['password']
    email = req['email']

    try:
        credential_checking(password, email)
    except MsgException as exception:
        return construct_msg(exception), 400

    user = User(username=username, email=email)
    user.set_password(password)
    try:
        db.session.add(user)
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        return construct_msg('User %s already exist' % username), 401
    else:
        db.session.commit()
    return jsonify(
        {'access_token': create_access_token(identity=user.username)}), 201


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    token = RevokedToken.query.filter_by(jti=jti).first()
    return not token is None


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
    db.session.flush()
    db.session.commit()
    return construct_msg('Logged out'), 200
