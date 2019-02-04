from .app import db
from .models.user import User
from flask import (
    Blueprint, request, abort, jsonify, g
)
from .utils.auth import generate_token, requires_auth
from sqlalchemy.exc import IntegrityError

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
            return jsonify({'access_token' : generate_token(user)}), 201
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
    return jsonify({'access_token' : generate_token(user)}), 201
