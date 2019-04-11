"""
Module for annotation end points
"""

import json

from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import (get_jwt_identity, jwt_required)

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
    fields_to_check = ['project_id', 'image_id', 'labels']
    for field_to_check in fields_to_check:
        if field_to_check not in req:
            abort(400, 'Missing %s in json' % field_to_check)
    project = maybe_get_project(req['project_id'])
    image = Image.query.filter_by(id=req['image_id'],
                                  project_id=project.id).first()
    if not image:
        abort(400, 'Invalid image id')

    # Validate labels
    labels = req['labels']
    fields_to_check = ['label_id']
    for label_obj in labels:
        for field_to_check in fields_to_check:
            if field_to_check not in label_obj:
                abort(400, 'Missing %s in label' % field_to_check)
        label_id = label_obj['label_id']
        label = Label.query.filter_by(id=label_id,
                                      project_id=project.id).first()
        if not label:
            abort(400, 'label id %d not in project %s' % (
                label_id, project.project_name))

    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()

    for label_obj in labels:
        data = str.encode(json.dumps(label_obj))
        label_id = label_obj['label_id']
        label = Label.query.filter_by(id=label_id,
                                      project_id=project.id).first()

        annotation = Annotation.query.filter_by(label_id=label_id,
                                                image_id=image.id).first()
        if annotation:
            annotation.data = data
        else:
            annotation = Annotation(data=data, image_id=image.id,
                                    label_id=label_id, vector=b'')
            project.annotations.append(annotation)
            image.is_annotated = True
            image.annotations.append(annotation)
            label.annotations.append(annotation)
            user.annotations.append(annotation)
    db.session.commit()
    return construct_msg('Annotation saved successfully'), 200


@bp.route('/<int:label_id>/<int:image_id>/', methods=['GET'])
@jwt_required
def get_annotation(label_id, image_id):
    label = Label.query.filter_by(id=label_id).first()
    if not label:
        abort(400, 'Invalid label id')
    project = maybe_get_project(label.project_id)
    image = Image.query.filter_by(id=image_id,
                                  project_id=project.id).first()
    if image is None:
        abort(400, 'Invalid image id')
    annotation = Annotation.query.filter_by(project_id=project.id,
                                            image_id=image.id,
                                            label_id=label.id).first()
    if not annotation:
        abort(400, 'Annotation not found')
    return jsonify(json.loads(annotation.data)), 200
