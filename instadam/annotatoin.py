"""
Module for annotation end points
"""

import base64

from PIL import Image
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import (jwt_required)
from sqlalchemy.exc import IntegrityError

from instadam.app import db
from instadam.models.annotation import Annotation
from instadam.models.image import Image
from instadam.models.label import Label
from instadam.utils import construct_msg
from instadam.utils.get_project import maybe_get_project

bp = Blueprint('annotation', __name__, url_prefix='/annotation')


@bp.route('/', methods=['POST'])
@jwt_required
def upload_annotation():
    req = request.get_json()
    ids_to_check = ['project_id', 'label_id', 'image_id']
    for id_to_check in ids_to_check:
        if id_to_check not in req:
            abort(400, 'Missing %s in json' % id_to_check)
    project = maybe_get_project(req['project_id'])
    label = Label.query.filter_by(id=req['label_id'],
                                  project_id=project.id).first()
    image = Image.query.filter_by(id=req['image'],
                                  project_id=project.id).first()
    if not (label and image):
        abort(400, 'Invalid label or image')
    if 'annotation' not in request.files:
        abort(400, 'Missing annotation file')

    file = request.files['annotation']
    orig_image = Image.open(image.image_path)
    binary_annotation = file.read()
    annotation_img = Image.open(binary_annotation)

    if not orig_image.shape[:2] == annotation_img.shape[:2]:
        abort(400, 'Annotation shape does not match image')
    annotation = Annotation(data=binary_annotation)
    project.annotations.append(annotation)
    image.annotations.append(annotation)
    label.annotations.append(annotation)
    try:
        db.session.add(label)
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        abort(400, 'Failed to add annotation')
    else:
        db.session.commit()
    return construct_msg('Annotation added successfully'), 200


@bp.route('/', methods=['GET'])
@jwt_required
def upload_annotation():
    req = request.get_json()
    ids_to_check = ['label_id', 'image_id']
    for id_to_check in ids_to_check:
        if id_to_check not in req:
            abort(400, 'Missing %s in json' % id_to_check)
    label = Label.query.filter_by(id=req['label_id'], ).first()
    if not label:
        abort(400, 'Invalid label id')
    project = maybe_get_project(label.project_id)
    image = Image.query.filter_by(id=req['image'],
                                  project_id=project.id).first()
    if image is None:
        abort(400, 'Invalid image id')
    annotation = Annotation.query.filter_by(project_id=project.id,
                                            image_id=image.id,
                                            label_id=label.id)
    if not annotation:
        abort(400, 'Annotation not found')
    encoded_string = base64.encodebytes(annotation.data)
    return jsonify({'base64': encoded_string}), 200
