"""Module related to loading images
"""

from flask import Blueprint, abort, request, jsonify
from flask_jwt_extended import (get_jwt_identity, jwt_required)
from sqlalchemy.exc import IntegrityError

from instadam.app import db
from instadam.models.image import Image
from instadam.models.project import Project
from instadam.models.project_permission import (AccessTypeEnum,
                                                ProjectPermission)
from instadam.models.user import PrivilegesEnum, User
from instadam.utils import construct_msg

bp = Blueprint('project', __name__, url_prefix='/project')

k = 5  # Fixed max number of images to return in response


@bp.route('/new', methods=['GET'])
@jwt_required
def get_unannotated_images():
    """
    Get unannotated images across ALL projects so that user (annotator) can see images to annotate
    NOTE: Only returning a fixed number of images (k=5) for Iteration 3
    """
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    unannotated_images = Image.query.filter_by(is_annotated=False).all()[0:k]
    print(unannotated_images)

    unannotated_images_res = []
    for unannotated_image in unannotated_images:
        unannotated_image_res = {}
        unannotated_image_res['id'] = unannotated_image.id
        unannotated_image_res['name'] = unannotated_image.image_name
        unannotated_image_res['path'] = unannotated_image.image_path
        unannotated_image_res['project_id'] = unannotated_image.project_id
        unannotated_images_res.append(unannotated_image_res)

    return jsonify({
        'email': user.email,
        'unannotated_images': unannotated_images_res
    })


@bp.route('/<project_id>/image/<image_id>')
@jwt_required
def get_project_image(project_id, image_id):
    """
    Get images with image_id that exists in project with project_id
    NOTE: Only returning a fixed number of images (k=5) for Iteration 3

    Args:
        project_id: The id of the project
        image_id: The id of the image to return
    """
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    image = Image.query.filter_by(id=image_id, project_id=project_id).all()[0]
    print(image)

    return jsonify({
        'username': user.email,
        'id': image.id,
        'path': image.image_path,
        'project_id': image.project_id
    })


@bp.route('/<project_id>/images')
@jwt_required
def get_project_images(project_id):
    """
    Get all images (annotated and unannotated) of project with project_id
    NOTE: Only returning a fixed number of images (k=5) for Iteration 3

    Args:
        project_id: The id of the project
    """
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    project_images = Image.query.filter_by(project_id=project_id).all()[0:k]
    print(project_images)

    project_images_res = []
    for project_image in project_images:
        project_image_res = {}
        project_image['id'] = project_image.id
        project_image['path'] = project_image.image_path
        project_image['project_id'] = project_image.project_id
        project_images_res.append(project_image_res)

    return jsonify({
        'username': user.email,
        'project_images': project_images_res
    })
