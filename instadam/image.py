"""Module related to uploading image
"""

from flask import Blueprint, abort, request
from flask_jwt_extended import (get_jwt_identity, jwt_required)
from sqlalchemy.exc import IntegrityError

from instadam.app import db
from instadam.models.image import Image
from instadam.models.project_permission import (AccessTypeEnum,
                                                ProjectPermission)
from instadam.models.user import PrivilegesEnum, User
from instadam.utils import construct_msg

bp = Blueprint('image', __name__, url_prefix='/image')


@bp.route('/upload/<project_id>', methods=['POST'])
@jwt_required
def upload_image(project_id):
    """
    Upload image to a project

    Args:
        project_id: The id of the project
    """
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
    if 'image' in request.files:
        file = request.files['image']
        project = permission.project
        image = Image(project_id=project.id)
        image.save_image_to_project(file)
        project.images.append(image)
        try:
            db.session.add(image)
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            abort(400, 'Failed to add image')
        else:
            db.session.commit()
        return construct_msg('Image added successfully'), 200
    else:
        abort(400, 'Missing \'image\' in request')
