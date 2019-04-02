from instadam.models.user import User, PrivilegesEnum
from flask import abort


def check_user_admin_privilege(username):
    user = User.query.filter_by(username=username).first()
    if user.privileges != PrivilegesEnum.ADMIN:
        abort(401, 'Logged in user is not an admin.')
    return user
