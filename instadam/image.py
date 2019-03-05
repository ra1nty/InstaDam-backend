"""Module related to uploading image
"""

from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import (get_jwt_identity, jwt_required)
from sqlalchemy.exc import IntegrityError

from instadam.app import db
from instadam.models.image import Image
from instadam.models.project_permission import (AccessTypeEnum,
                                                ProjectPermission)
from instadam.models.user import PrivilegesEnum, User
from instadam.utils import construct_msg

bp = Blueprint('image', __name__, url_prefix='/image')

k = 5  # Fixed max number of images to return in response


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


@bp.route('/unannotated', methods=['GET'])
@jwt_required
def get_unannotated_images():
    """
    Get unannotated images across ALL projects so that user (annotator) can
    see images to annotate
    NOTE: Only returning a fixed number of images (k=5) for Iteration 3
    """
    unannotated_images = Image.query.filter_by(is_annotated=False).all()[0:k]
    if not unannotated_images:
        return jsonify({'unannotated_images': []}), 200

    unannotated_images_res = []
    for unannotated_image in unannotated_images:
        unannotated_image_res = {}
        unannotated_image_res['id'] = unannotated_image.id
        unannotated_image_res['name'] = unannotated_image.image_name
        unannotated_image_res['path'] = unannotated_image.image_path
        unannotated_image_res['project_id'] = unannotated_image.project_id
        unannotated_images_res.append(unannotated_image_res)

    return jsonify({'unannotated_images': unannotated_images_res}), 200


@bp.route('/<image_id>/project/<project_id>')
@jwt_required
def get_project_image(project_id, image_id):
    """
    Get images with image_id that exists in project with project_id
    NOTE: Only returning a fixed number of images (k=5) for Iteration 3

    Args:
        project_id: The id of the project
        image_id: The id of the image to return
    """
    image = Image.query.filter_by(id=image_id, project_id=project_id).all()
    if image.first() == None:
        abort(
            404, 'No image in project of id=%s found with id=%s' % (project_id,
                                                                    image_id))
    else:
        image = image[0]

    return jsonify({
        'id': image.id,
        'path': image.image_path,
        'project_id': image.project_id
    }), 200


@bp.route('/project/<project_id>')
@jwt_required
def get_project_images(project_id):
    """
    Get all images (annotated and unannotated) of project with project_id
    NOTE: Only returning a fixed number of images (k=5) for Iteration 3

    Args:
        project_id: The id of the project
    """
    project_images = Image.query.filter_by(project_id=project_id).all()[0:k]
    if not project_images:
        return jsonify({'project_images': []}), 200

    project_images_res = []
    for project_image in project_images:
        project_image_res = {}
        project_image_res['id'] = project_image.id
        project_image_res['name'] = project_image.image_name
        project_image_res['path'] = project_image.image_path
        project_image_res['project_id'] = project_image.project_id
        project_images_res.append(project_image_res)

    return jsonify({'project_images': project_images_res}), 200
