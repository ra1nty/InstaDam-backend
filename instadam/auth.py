from .app import db
from .models.user import User
from flask import (
    Blueprint, request, abort, jsonify, g
)
from .utils.auth import generate_token, requires_auth
from sqlalchemy.exc import IntegrityError
from email.utils import parseaddr

bp = Blueprint('auth', __name__, url_prefix='')

# Raises IntegrityError exception if values for request fields do not follow certain constraints
def credential_checking(password, email):
    # Check password
    if len(password) < 8:
        raise IntegrityError("Password should be longer than 8 characters.", password, "")
    has_digit = any([c.isdigit() for c in password])
    if not has_digit:
        raise IntegrityError("Password must have at least one digit.", password, "")
    has_upper = any([c.isupper() for c in password])
    if not has_upper:
        raise IntegrityError("Password must have at least one uppercase letter.", password, "")
    
    # Check email
    if parseaddr(email) == ('', '') or '@' not in email:
        raise IntegrityError("Please enter a valid email addresss.", email, "")


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
    
    username = req['username']
    password = req['password']
    email = req['email']

    try:
        credential_checking(password, email)
    except IntegrityError:
        abort(401)

    user = User(username=username, email=email)
    user.set_password(password)
    try:
        db.session.add(user)
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        abort(401)
    else:
        db.session.commit()
    return jsonify({'access_token' : generate_token(user)}), 201
