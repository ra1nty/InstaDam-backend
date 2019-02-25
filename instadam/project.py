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


@bp.route('/new', methods=['GET'])
@jwt_required
def get_unannotated_images():
    """
    Get unannotated images across ALL projects so that user (annotator) can see images to annotate
    NOTE: Only returning a fixed number of images (k=5) for Iteration 3
    """
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    return jsonify({'username': current_user})


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
    return jsonify({'username': current_user})


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
    return jsonify({'username': current_user})