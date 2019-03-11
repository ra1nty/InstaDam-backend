import os

from flask import Blueprint, abort, jsonify, request
from flask import current_app as app
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import DatabaseError, IntegrityError

from instadam.models.image import Image
from instadam.models.label import Label
from instadam.models.project_permission import AccessTypeEnum, ProjectPermission
from instadam.models.user import PrivilegesEnum, User
from instadam.utils import construct_msg
from instadam.utils.get_project import maybe_get_project
from .app import db
from .models.project import Project

bp = Blueprint('project', __name__, url_prefix='')


@bp.route('/project', methods=['POST'])
@jwt_required
def create_project():
    """ Create a new project by the user currently signed in

    Create a new project entry in the database and a new folder in the
    filesystem
    to hold image dataset upon receiving a `POST`request to the `/project` entry
    point. User must be signed in as an ADMIN and must provide a `project name`
    to create a new project.

    Must supply a jwt-token to verify user status and extract `user_id`.
    `project name` must be unique.

    Raises:
        400 Error if project name is not specified
        401 Error if not logged in
        401 Error if user is not an ADMIN
        400 Error if project name already exists in the database


    Returns:
        201 if success. Will also return `project_id`.
    """

    req = request.get_json()
    if 'project_name' not in req:
        abort(400, 'Project name must be included.')

    # check user identity and privilege
    identity = get_jwt_identity()
    user = User.query.filter_by(username=identity).first()
    if user.privileges != PrivilegesEnum.ADMIN:
        abort(401, 'User does not have the privilege to create a project.')

    project_name = req['project_name']
    user_id = user.id
    project = Project(project_name=project_name, created_by=user_id)
    try:
        db.session.add(project)
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        abort(
            400, 'Duplicate project name. '
                 'Please provide a different project name.')
    else:
        # if able to add project to db, try add project_permission
        # creator is granted with READ_WRITE privilege
        project_permission = ProjectPermission(
            access_type=AccessTypeEnum.READ_WRITE,
            user_id=user_id,
            project_id=project.id)
        try:
            db.session.add(project_permission)
            db.session.flush()
        except DatabaseError:
            db.session.rollback()
            abort(400, 'Cannot update project permission for user.')

    db.session.commit()

    # create project directory
    project_dir = os.path.join(app.config['STATIC_STORAGE_DIR'],
                               str(project.id))
    os.makedirs(project_dir)

    return jsonify({
        'msg': 'project added successfully',
        'project_id': project.id
    }), 201


@bp.route('/projects/<project_id>/unannotated', methods=['GET'])
@jwt_required
def get_unannotated_images(project_id):
    """
    Get unannotated images across ALL projects so that user (annotator) can
    see images to annotate
    NOTE: Only returning a fixed number of images (k=5) for Iteration 3
    """

    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()

    project_exists = Project.query.filter_by(id=project_id).first()
    if project_exists is None:
        abort(404, 'Project with id=%s does not exist' % (project_id))

    has_permission = ProjectPermission.query.filter_by(
        user_id=user.id, project_id=project_id).first()
    if has_permission is None:
        abort(
            401,
            'User does not have the privilege to view the unannotated images '
            'of project with id=%s'
            % (project_id))

    unannotated_images = Image.query.filter_by(
        is_annotated=False, project_id=project_id).all()
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


@bp.route('/projects/<project_id>/images')
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

    project_exists = Project.query.filter_by(id=project_id).first()
    if project_exists is None:
        abort(404, 'Project with id=%s does not exist' % (project_id))

    has_permission = ProjectPermission.query.filter_by(
        user_id=user.id, project_id=project_id).first()
    if has_permission is None:
        abort(
            401,
            'User does not have the privilege to view the images of project '
            'with id=%s'
            % (project_id))

    project_images = Image.query.filter_by(project_id=project_id).all()
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


@bp.route('/project/<project_id>/labels', methods=['POST'])
@jwt_required
def add_label(project_id):
    project = maybe_get_project(project_id)
    req = request.get_json()
    if not 'label_name' in req:
        abort(400, 'Missing label name')
    label_name = req['label_name']
    label = Label(label_name=label_name)
    project.labels.append(label)
    try:
        db.session.add(label)
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        abort(400, 'Failed to add image')
    else:
        db.session.commit()
    return construct_msg('Label added successfully'), 200
