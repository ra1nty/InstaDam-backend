"""Module related to searching for users
"""
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import (jwt_required)
from instadam.app import db
from sqlalchemy.exc import IntegrityError

from instadam.models.user import PrivilegesEnum, User

bp = Blueprint('project', __name__, url_prefix='/users')


@bp.route('/search/<user_query>', methods=['POST'])
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
    users = User.query.filter(User.username.like(user_query_str)).all()

    if not users:
        return jsonify({'users': []}), 200

    users_res = []
    for user in users:
        user_res = {}
        user_res['username'] = user.username
        user_res['created_at'] = user.created_at
        user_res['priveleges'] = user.priveleges
        users_res.append(user_res)

    return jsonify({'users': users_res}), 200
