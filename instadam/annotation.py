"""
Module for annotation end points
"""

import base64
from io import BytesIO

import PIL.Image
import numpy as np
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import (get_jwt_identity, jwt_required)
from sqlalchemy.exc import IntegrityError

from instadam.app import db
from instadam.models.annotation import Annotation
from instadam.models.image import Image
from instadam.models.label import Label
from instadam.models.user import User
from instadam.utils import construct_msg
from instadam.utils.get_project import maybe_get_project

bp = Blueprint('annotation', __name__, url_prefix='/annotation')


@bp.route('/', methods=['POST'])
@jwt_required
def upload_annotation():
    req = request.get_json()
    ids_to_check = ['project_id', 'label_id', 'image_id', 'annotation']
    for id_to_check in ids_to_check:
        if id_to_check not in req:
            abort(400, 'Missing %s in json' % id_to_check)
    project = maybe_get_project(req['project_id'])
    label = Label.query.filter_by(id=req['label_id'],
                                  project_id=project.id).first()
    image = Image.query.filter_by(id=req['image_id'],
                                  project_id=project.id).first()
    if not (label and image):
        abort(400, 'Invalid label or image')

    orig_image = np.asarray(PIL.Image.open(image.image_path))
    binary_annotation = base64.b64decode(req['annotation'])
    annotation_img = np.asarray(PIL.Image.open(BytesIO(binary_annotation)))

    if not orig_image.shape[:2] == annotation_img.shape[:2]:
        abort(400, 'Annotation shape does not match image')
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()

    byte_data = b''

    try:
        byte_data = base64.b64decode(req['annotation'])
    except Exception as e:
        abort(400, str(e))

    annotation = Annotation(data=byte_data, image_id=image.id,
                            label_id=label.id)
    project.annotations.append(annotation)
    image.annotations.append(annotation)
    label.annotations.append(annotation)
    user.annotations.append(annotation)
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
def get_annotation():
    req = request.get_json()
    ids_to_check = ['label_id', 'image_id']
    for id_to_check in ids_to_check:
        if id_to_check not in req:
            abort(400, 'Missing %s in json' % id_to_check)
    label = Label.query.filter_by(id=req['label_id'], ).first()
    if not label:
        abort(400, 'Invalid label id')
    project = maybe_get_project(label.project_id)
    image = Image.query.filter_by(id=req['image_id'],
                                  project_id=project.id).first()
    if image is None:
        abort(400, 'Invalid image id')
    annotation = Annotation.query.filter_by(project_id=project.id,
                                            image_id=image.id,
                                            label_id=label.id).first()
    if not annotation:
        abort(400, 'Annotation not found')
    base64_str = base64.b64encode(annotation.data).decode('utf-8')
    return jsonify({'base64': base64_str}), 200
