"""Module related to loading images
"""

from flask import Blueprint, abort, request, jsonify
from flask_jwt_extended import (get_jwt_identity, jwt_required)
from sqlalchemy.exc import IntegrityError

from instadam.app import db
from instadam.models.image import Image
from instadam.models.project import Project
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
    unannotated_images = Image.query.filter_by(is_annotated=False).all()[0:k]
    if len(unannotated_images) == 0:
        return jsonify({'unannotated_images': []})

    unannotated_images_res = []
    for unannotated_image in unannotated_images:
        unannotated_image_res = {}
        unannotated_image_res['id'] = unannotated_image.id
        unannotated_image_res['name'] = unannotated_image.image_name
        unannotated_image_res['path'] = unannotated_image.image_path
        unannotated_image_res['project_id'] = unannotated_image.project_id
        unannotated_images_res.append(unannotated_image_res)

    return jsonify({'unannotated_images': unannotated_images_res})


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
    image = Image.query.filter_by(id=image_id, project_id=project_id).all()
    if len(image) == 0:
        abort(
            404, 'No image in project of id=' + str(project_id) +
            ' found with id=' + str(image_id))
    else:
        image = image[0]

    return jsonify({
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
    project_images = Image.query.filter_by(project_id=project_id).all()[0:k]
    if len(project_images) == 0:
        return jsonify({'project_images': []})

    project_images_res = []
    for project_image in project_images:
        project_image_res = {}
        project_image_res['id'] = project_image.id
        project_image_res['name'] = project_image.image_name
        project_image_res['path'] = project_image.image_path
        project_image_res['project_id'] = project_image.project_id
        project_images_res.append(project_image_res)

    return jsonify({'project_images': project_images_res})
