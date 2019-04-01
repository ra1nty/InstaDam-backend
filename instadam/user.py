from flask import Blueprint, abort, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from instadam.app import db
from instadam.models.user import PrivilegesEnum, User
from instadam.utils import check_json, construct_msg

bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route('/privilege', method=['PUT'])
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
    Valid privileges are: "annotator", "admin"
    Returns:
        401 if: current user is not logged in
        403 if: current user is not admin
        400 if: requested user is not found, privilege name is not valid
        200 if: updated successfully

    """
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if user.privileges != PrivilegesEnum.ADMIN:
        abort(403, 'Logged in user is not admin')

    json = request.get_json()
    check_json(json, ('username', 'privilege'))

    username = json['username']

    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(400, 'User %s not found' % username)

    privilege_map = {'admin': PrivilegesEnum.ADMIN,
                     'annotator': PrivilegesEnum.ANNOTATOR}

    privilege = json['privilege']
    if privilege not in privilege_map:
        abort(400, 'Invalid privilege %s' % privilege)

    user.privileges = privilege_map[privilege]
    db.session.commit()

    return construct_msg(
        'Privilege updated to %s successfully' % privilege), 200
