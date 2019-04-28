from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from instadam.app import db
from instadam.auth import credential_checking, email_checking
from instadam.models.user import PrivilegesEnum, User
from instadam.utils import check_json, construct_msg
from instadam.utils.user_identification import check_user_admin_privilege

bp = Blueprint('user', __name__, url_prefix='')


@bp.route('/users/search', methods=['GET'])
@jwt_required
def query_users():
    """
    Upload image to a project

    Args:
        user_query -- query to search for specific user(s)

    Returns:
        list of users that satisfy the query
    """

    user_query = request.args.get('q')

    current_user = get_jwt_identity()
    check_user_admin_privilege(current_user)

    user_query_str = '%' + user_query + '%'
    users = User.query.filter(
        or_(
            User.username.ilike(user_query_str),
            User.email.ilike(user_query_str))).all()

    if not users:
        return jsonify({'users': []}), 200

    users_res = []
    for user in users:
        user_res = {}
        user_res['username'] = user.username
        user_res['email'] = user.email
        user_res['created_at'] = str(user.created_at)
        user_res['privileges'] = str(user.privileges)
        users_res.append(user_res)

    return jsonify({'users': users_res}), 200


@bp.route('/user/privilege/', methods=['PUT'])
@jwt_required
def change_privilege():
    """
    Update privilege of a user.
    Requires the requester to login and be an admin.
    Example json:
    {
        "username": "someone",
        "privilege": "admin",
    }
    or
    {
        "username": "someone",
        "privilege": "annotator",
    }
    Valid privileges are "annotator", "admin"
    Returns:
        401 if current user is not logged in
        403 if current user is not admin
        400 if requested user is not found, privilege name is not valid
        200 if updated successfully

    """
    current_user = get_jwt_identity()
    check_user_admin_privilege(current_user)

    json = request.get_json()
    check_json(json, ('username', 'privilege'))

    username = json['username']

    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(400, 'User %s not found' % username)

    privilege_map = {
        'admin': PrivilegesEnum.ADMIN,
        'annotator': PrivilegesEnum.ANNOTATOR
    }

    privilege = json['privilege']
    if privilege not in privilege_map:
        abort(400, 'Invalid privilege %s' % privilege)

    user.privileges = privilege_map[privilege]
    db.session.commit()

    return construct_msg(
        'Privilege updated to %s successfully' % privilege), 200


@bp.route('/user/', methods=['PUT'])
@jwt_required
def update_info():
    """
    Allow user to update personal info: username, email, and password

    Example input json:
    {
        "username": "admin1",
        "current_password": "Password0",
        "email": "test@test.com",
        "password": "Password1234"
    }

    Will only update provided fields. "current_password" is required.

    Raises:
        400 if new password format is incorrect
        400 if new email format is incorrect
        400 if username or email is duplicate
        401 if the current password is not correct
    """
    current_user = get_jwt_identity()
    json = request.get_json()
    user = User.query.filter_by(username=current_user).first()
    check_json(json, ['current_password'])
    if not user.verify_password(json['current_password']):
        abort(401, 'Current password incorrect')
    new_password = json.get('password', None)
    if new_password and credential_checking(new_password):
        user.set_password(new_password)

    new_email = json.get('email', None)
    if new_password and email_checking(new_email):
        user.email = new_email

    new_username = json.get('username', None)
    if new_username:
        user.username = new_username

    try:
        db.session.commit()
    except IntegrityError:
        abort(400, 'Username or email already exist')

    return construct_msg('Successfully updated'), 200
