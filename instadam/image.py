"""Module related to uploading image
"""
import multiprocessing
import os
import uuid
from zipfile import ZipFile

from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import (jwt_required)
from instadam.app import db
from instadam.models.image import Image, VALID_IMG_EXTENSIONS
from instadam.utils import construct_msg
from instadam.utils.file import (get_project_dir,
                                 parse_and_validate_file_extension)
from sqlalchemy.exc import IntegrityError

from instadam.utils.get_project import maybe_get_project

bp = Blueprint('image', __name__, url_prefix='/image')


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
            name_map[image_name] = image.image_path

        zip_file.close()
        multiprocessing.Process(
            target=unzip_process, args=(zip_path, name_map)).start()
        return (
            construct_msg('Zip uploaded successfully, please wait for unzip'),
            200)
    else:
        abort(400, 'Missing \'zip\' in request')


@bp.route('/<image_id>')
@jwt_required
def get_project_image(image_id):
    """
    Get images with image_id that exists in project with project_id

    Args:
        project_id: The id of the project
        image_id: The id of the image to return
    """
    image = Image.query.filter_by(id=image_id).first()
    if image == None:
        abort(404, 'No image found with id=%s' % (image_id))

    return jsonify({
        'id': image.id,
        'path': image.image_path,
        'project_id': image.project_id
    }), 200
