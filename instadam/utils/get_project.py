from flask_jwt_extended import get_jwt_identity
from werkzeug.exceptions import abort

from instadam.models.project_permission import AccessTypeEnum, ProjectPermission
from instadam.models.user import PrivilegesEnum, User


def maybe_get_project(project_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if user.privileges == PrivilegesEnum.ANNOTATOR:
        abort(401, 'User is not Admin')
    permission = ProjectPermission.query.filter_by(
        project_id=project_id,
        user_id=user.id,
        access_type=AccessTypeEnum.READ_WRITE).first()
    if permission is None:
        abort(401, 'User does not have permission to add image to this project')
    return permission.project


def maybe_get_project_read_only(project_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    permission = ProjectPermission.query.filter(
        (ProjectPermission.user_id == user.id)
        & (ProjectPermission.project_id == project_id)).filter(
        (ProjectPermission.access_type == AccessTypeEnum.READ_ONLY)
        | (ProjectPermission.access_type == AccessTypeEnum.READ_WRITE)).first()
    if permission is None:
        abort(401,
              'User does not have permission to read images of this project')
    return permission.project
