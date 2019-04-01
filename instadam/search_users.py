"""Module related to searching for users
"""
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from instadam.app import db
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from instadam.models.user import PrivilegesEnum, User

bp = Blueprint('search_users', __name__, url_prefix='/users')


@bp.route('/search?q=<user_query>', methods=['GET'])
@jwt_required
def query_users(user_query):
    """
    Upload image to a project

    Args:
        user_query: query to search for specific user(s)

    Returns:
        list of users that satisfy the query
    """

    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if user.privileges != PrivilegesEnum.ADMIN:
        abort(401, 'User does not have the privilege to search for users.')

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
