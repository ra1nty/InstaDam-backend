"""Module related to searching for users
"""
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import or_

from instadam.models.user import PrivilegesEnum, User
from instadam.utils.user_identification import check_user_admin_privilege

bp = Blueprint('search_users', __name__, url_prefix='/users')


@bp.route('/search', methods=['GET'])
@jwt_required
def query_users():
    """
    Upload image to a project

    Args:
        user_query: query to search for specific user(s)

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
