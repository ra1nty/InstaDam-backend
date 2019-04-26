from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import or_

from instadam.app import db
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
