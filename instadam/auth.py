from .app import db, jwt
from .models.user import User
from .models.revoked_token import RevokedToken
from flask import (Blueprint, request, abort, jsonify, g)
from .utils.auth import generate_token, requires_auth
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (JWTManager, jwt_required, get_jwt_identity,
                                create_access_token, create_refresh_token,
                                jwt_refresh_token_required, get_raw_jwt)

bp = Blueprint('auth', __name__, url_prefix='')


@bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint for application

    Take POST data as json with userame and password.
    Return a json web token as access token.

    Example:
        POST /login
    """
    req = request.get_json()
    if 'username' not in req or 'password' not in req:
        abort(400)
    user = User.query.filter_by(username=req['username']).first()
    if user is not None:
        if user.verify_password(req['password']):
            return jsonify({
                'access_token':
                create_access_token(identity=user.username)
            }), 201
    abort(401)


@bp.route('/register', methods=['POST'])
def register():
    """
    User register endpoint for application

    Take POST data as json with userame and password.
    Return a json web token as access token.

    Example:
        POST /register
    """
    req = request.get_json()
    if 'username' not in req or 'password' not in req or 'email' not in req:
        abort(400)
    user = User(username=req['username'], email=req['email'])
    user.set_password(req['password'])
    try:
        db.session.add(user)
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        abort(401)
    else:
        db.session.commit()
    return jsonify({
        'access_token': create_access_token(identity=user.username)
    }), 201


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    token = RevokedToken.query.filter_by(jti=jti).first()
    return not token is None


@bp.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    token = RevokedToken(jti=jti)
    db.session.add(token)
    db.session.flush()
    db.session.commit()
    return jsonify({'msg': 'Logged out'}), 200
