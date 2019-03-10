"""Module related to uploading image
"""
import multiprocessing
import os
import uuid
from zipfile import ZipFile

from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import (get_jwt_identity, jwt_required)
from instadam.app import db
from instadam.models.image import Image, VALID_IMG_EXTENSIONS
from instadam.models.project_permission import (AccessTypeEnum,
                                                ProjectPermission)
from instadam.models.user import PrivilegesEnum, User
from instadam.utils import construct_msg
from instadam.utils.file import (get_project_dir,
                                 parse_and_validate_file_extension)
from sqlalchemy.exc import IntegrityError

bp = Blueprint('image', __name__, url_prefix='/image')

k = 5  # Fixed max number of images to return in response


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


@bp.route('/upload/<project_id>', methods=['POST'])
@jwt_required
def upload_image(project_id):
    """
    Upload image to a project

    Args:
        project_id: The id of the project
    """
    project = maybe_get_project(project_id)
    if 'image' in request.files:
        file = request.files['image']
        project = project
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


def unzip_process(zip_path, name_map):
    zip_file = ZipFile(zip_path)
    for name, hashed_name in name_map.items():
        image = zip_file.read(name)
        with open(hashed_name, 'wb') as f:
            f.write(image)
    try:
        os.remove(zip_path)
    except OSError:
        pass


@bp.route('/upload/zip/<project_id>', methods=['POST'])
@jwt_required
def upload_zip(project_id):
    def filter_condition(name):
        split = name.lower().split('.')
        return split and split[-1] in VALID_IMG_EXTENSIONS

    project = maybe_get_project(project_id)
    project_dir = get_project_dir(project)
    if 'zip' in request.files:
        file = request.files['zip']
        extension = parse_and_validate_file_extension(file.filename, {'zip'})
        new_file_name = '%s.%s' % (str(uuid.uuid4()), extension)
        zip_path = os.path.join(project_dir, new_file_name)
        file.save(zip_path)
        zip_file = ZipFile(zip_path)
        image_names = zip_file.namelist()
        name_map = {}
        for image_name in filter(filter_condition, image_names):
            if image_name in name_map:
                continue
            image = Image(project_id=project.id)
            image.save_empty_image(image_name)
            project.images.append(image)
            try:
                db.session.add(image)
                db.session.flush()
            except IntegrityError:
                db.session.rollback()
                abort(400, 'Failed to add image')
            else:
                db.session.commit()
            name_map[image_name] = image.image_name

        zip_file.close()
        multiprocessing.Process(target=unzip_process,
                                args=(zip_path, name_map)).start()
        return (construct_msg(
            'Zip uploaded successfully, please wait for unzip'), 200)
    else:
        abort(400, 'Missing \'zip\' in request')


@bp.route('/new', methods=['GET'])
@jwt_required
def get_unannotated_images():
    """
    Get unannotated images across ALL projects so that user (annotator) can
    see images to annotate
    NOTE: Only returning a fixed number of images (k=5) for Iteration 3
    """
    unannotated_images = Image.query.filter_by(is_annotated=False).all()[0:k]
    if len(unannotated_images) == 0:
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
        abort(404, 'No image in project of id=%s found with id=%s' % (
            project_id, image_id))
    else:
        image = image[0]

    return jsonify({
        'id': image.id,
        'path': image.image_path,
        'project_id': image.project_id}), 200


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
