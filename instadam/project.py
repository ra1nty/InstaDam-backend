import os
import shutil
from string import hexdigits

from flask import Blueprint, abort, jsonify, request
from flask import current_app as app
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import DatabaseError, IntegrityError

from instadam.models.image import Image
from instadam.models.label import Label
from instadam.models.project_permission import AccessTypeEnum, ProjectPermission
from instadam.models.user import PrivilegesEnum, User
from instadam.utils import check_json, construct_msg
from instadam.utils.get_project import (maybe_get_project,
                                        maybe_get_project_read_only)
from instadam.utils.user_identification import check_user_admin_privilege
from .app import db
from .models.project import Project

from instadam.models.message import MessageTypeEnum, Message
from instadam.utils import check_json

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
    check_json(req, ['project_name'])

    # check user identity and privilege
    identity = get_jwt_identity()
    user = check_user_admin_privilege(identity)

    project_name = req['project_name']
    user_id = user.id
    project = Project(project_name=project_name, created_by=user_id)

    try:
        db.session.add(project)
        db.session.flush()  # To make sure no duplicates exist in db
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
        user.project_permissions.append(project_permission)
        project.permissions.append(project_permission)
        try:
            db.session.add(project_permission)
        except DatabaseError:
            db.session.rollback()
            abort(400, 'Cannot update project permission for user.')

    db.session.commit()

    # create project directory
    project_dir = os.path.join(app.config['STATIC_STORAGE_DIR'],
                               str(project.id))
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)

    return jsonify({
        'msg': 'project added successfully',
        'project_id': project.id
    }), 201


@bp.route('/projects', methods=['GET'])
@jwt_required
def get_projects():
    """
    List all the project this user has access to.
    Returns:
        200, and a json list of projects
        {
            "id": 1,
            "is_admin": true,
            "name": "First Project"
        },
    """

    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    projects = []
    for project_permission in user.project_permissions:
        project_dict = {
            'id':
            project_permission.project.id,
            'name':
            project_permission.project.project_name,
            'is_admin':
            (user.privileges == PrivilegesEnum.ADMIN and
             project_permission.access_type == AccessTypeEnum.READ_WRITE)
        }
        projects.append(project_dict)
    return jsonify(projects), 200


@bp.route('/projects/<project_id>/unannotated', methods=['GET'])
@jwt_required
def get_unannotated_images(project_id):
    """
    Get unannotated images across ALL projects so that user (annotator) can
    see images to annotate

    Args:
        project_id -- ID of the project

    Returns:
        200 and a json object --
        {
            "unannotated_images": [
                {
                    "id": 1,
                    "is_annotated": false,
                    "name": "cf3179a2-6e0e-4dd8-938f-85e4147103ce.png",
                    "path": "static/1/cf3179a2-6e0e-4dd8-938f-85e4147103ce.png",
                    "project_id": 1
                },
            ]
        }
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
            'of project with id=%s' % (project_id))

    unannotated_images = Image.query.filter_by(
        is_annotated=False, project_id=project_id).all()
    if not unannotated_images:
        return jsonify({'unannotated_images': []}), 200

    unannotated_images_res = []
    for unannotated_image in unannotated_images:
        unannotated_image_res = {}
        unannotated_image_res['id'] = unannotated_image.id
        unannotated_image_res['name'] = unannotated_image.image_name
        unannotated_image_res['path'] = unannotated_image.image_url
        unannotated_image_res['project_id'] = unannotated_image.project_id
        unannotated_images_res.append(unannotated_image_res)

    return jsonify({'unannotated_images': unannotated_images_res}), 200


@bp.route('/projects/<project_id>/images')
@jwt_required
def get_project_images(project_id):
    """
    Get all images (annotated and unannotated) of project with project_id

    Args:
        project_id -- The id of the project

    Returns:
        200 and a json object --
        {
            "project_images": [
                {
                    "id": 1,
                    "is_annotated": false,
                    "name": "cf3179a2-6e0e-4dd8-938f-85e4147103ce.png",
                    "path": "static/1/cf3179a2-6e0e-4dd8-938f-85e4147103ce.png",
                    "project_id": 1
                },
            ]
        }
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
            'with id=%s' % project_id)

    project_images = Image.query.filter_by(project_id=project_id).all()
    if not project_images:
        return jsonify({'project_images': []}), 200

    project_images_res = []
    for project_image in project_images:
        project_image_res = dict()
        project_image_res['id'] = project_image.id
        project_image_res['name'] = project_image.image_name
        project_image_res['path'] = project_image.image_url
        project_image_res['project_id'] = project_image.project_id
        project_image_res['is_annotated'] = project_image.is_annotated
        project_images_res.append(project_image_res)

    return jsonify({'project_images': project_images_res}), 200


@bp.route('/project/<project_id>/labels', methods=['POST'])
@jwt_required
def add_label(project_id):
    """
    Add a label to the project

    Takes a json object --

    {
       "label_text": "first label",
       "label_color": "#12345"
    }

    Args:
        project_id -- ID of the project

    Returns:
        200 and json object
        {
            "msg": "Label added successfully"
        }

    """
    project = maybe_get_project(project_id)
    req = request.get_json()

    check_json(req, ['label_text', 'label_color'])

    label_name = req['label_text']
    label_color = req['label_color']
    if label_color[0] != '#' or not all(c in hexdigits
                                        for c in label_color[1:]):
        abort(400, 'Failed to add label, need color')
    label = Label(label_name=label_name, label_color=label_color)
    project.labels.append(label)
    try:
        db.session.add(label)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400, 'Failed to add label, label name should be unique')
    return jsonify({'label_id': label.id}), 200


@bp.route('/project/<project_id>/labels', methods=['GET'])
@jwt_required
def get_labels(project_id):
    """
    Get a list of labels in this project
    Does not need a request body

    Args:
        project_id -- The id of the project

    Returns:
        200 and a json object --
        {
            "labels": [
                {
                    "color": "#12345",
                    "label_id": 1,
                    "text": "first label"
                },
            ]
        }
    """
    project = maybe_get_project_read_only(project_id)
    labels = [{
        'color': label.label_color,
        'text': label.label_name,
        'label_id': label.id
    } for label in project.labels]
    return jsonify({'labels': labels}), 200


@bp.route('/project/<project_id>/permissions', methods=['PUT'])
@jwt_required
def update_user_permission(project_id):
    """ Grant a user with specified privilege to project

        Grant a user with specified privilege (READ_WRITE or READ_ONLY) to
        project
        upon receiving a `PUT`request to the `/project/<project_id>/permissions`
        entry point. User must be signed in as an ADMIN and have READ_WRITE
        permission to the project. User must provide a `username` to specify the
        user that will be granted permissions, and `access_type` to specify the
        type of privilege to grant.

        `access_type` takes a string of two values: `r` or `rw`, where `r` is
        `READ_ONLY` and `rw` is `READ_WRITE`

        Only user with `ADMIN` privilege can have `READ_WRITE` access to
        projects.
        That is, the user indicated by `username` should have an `ADMIN`
        privilege
        (as opposed to `ANNOTATOR` privilege)

        Must supply a jwt-token to verify user status and extract `user_id`.

        Raises:
            400 Error if username or access_type is not specified
            400 Error if access_type is not 'r' or 'rw'
            401 Error if not logged in
            401 Error if user is not an ADMIN
            401 Error if user does not have privilege to update permission
            403 Error if user indicated by `username` has only ANNOTATOR
            privilege
                but `access_type` is 'rw'
            404 Error if user with user_name does not exist

        Returns:
            201 if success. Will also return `project_id`.
        """

    project = maybe_get_project(project_id)  # check privilege and get project

    req = request.get_json()
    check_json(req, ('username', 'access_type'))  # check missing keys

    username = req['username']
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404, 'User with username=%s not found' % username)

    map_code_to_access_type = {
        'r': AccessTypeEnum.READ_ONLY,
        'rw': AccessTypeEnum.READ_WRITE,
    }
    if req['access_type'] not in map_code_to_access_type:
        abort(400, 'Not able to interpret access_type.')
    access_type = map_code_to_access_type[req['access_type']]

    # Check if user has already had some sort of permission to the project
    permission = ProjectPermission.query.filter(
        (ProjectPermission.user_id == user.id) &
        (ProjectPermission.project_id == project_id)).first()
    if permission is not None:
        permission.access_type = access_type
        db.session.commit()
        return construct_msg('Permission updated successfully'), 200

    new_permission = ProjectPermission(access_type=access_type)
    project.permissions.append(new_permission)
    user.project_permissions.append(new_permission)
    try:
        db.session.add(new_permission)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400, 'Update permission failed.')

    return construct_msg('Permission added successfully'), 201


@bp.route('/project/<project_id>/request', methods=['POST'])
@jwt_required
def request_permission(project_id):
    """ Request for specific permission to a project

        Request for specified privilege (READ_WRITE or READ_ONLY) to project
        upon receiving a `POST` request to the `/project/<project_id>/request`
        entry point. User must be signed in. User must provide a `message_type`
        to specify the privilege he or she is requesting for.

        `message_type` takes a string of two values: `r` or `rw`,
        where `r` is `READ_ONLY` and `rw` is `READ_WRITE`

        The request message will be sent to all admins of the project. Note that
        an annotator can also send a request of 'rw' permission. The decision of
        whether upgrading the ANNOTATOR to ADMIN and then granting 'rw' permission
        is left to the ADMIN.

        Must supply a jwt-token to verify user status and extract `user_id`.

        Raises:
            400 Error if message_type is not specified
            400 Error if message is not 'r' or 'rw'
            401 Error if not logged in
            404 Error if project does not exist

        Returns:
            201 if success. Will also return `project_id`.
        """

    req = request.get_json()
    check_json(req, ['message_type'])  # check missing keys

    project = Project.query.filter_by(id=project_id).first()
    if project is None:
        abort(404, 'Project with id=%s does not exist' % project_id)

    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()

    map_code_to_message_type = {
        'r': MessageTypeEnum.READ_ONLY_PERMISSION_REQUEST,
        'rw': MessageTypeEnum.READ_WRITE_PERMISSION_REQUEST,
    }

    if req['message_type'] not in map_code_to_message_type:
        abort(400, 'Not able to interpret message_type.')
    message_type = map_code_to_message_type[req['message_type']]

    # Get the list of admins to the project
    admins = []
    for permission in project.permissions:
        if permission.access_type == AccessTypeEnum.READ_WRITE:
            admins.append(permission.user)

    message = Message(type=message_type)
    try:
        db.session.add(message)
        user.sent_messages.append(message)
        for admin in admins:
            admin.received_messages.append(message)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400, 'Create message failed.')

    return construct_msg('Message sent successfully'), 200


@bp.route('/project/<project_id>', methods=['DELETE'])
@jwt_required
def delete_project(project_id):
    """
    Delete a project with specified project id. Doesn't require a body

    Args:
        project_id -- The ID of the project

    Raises:
        401 if
          * The project doesn't exist
          * Currently logged in user is not admin of this project (read write
            access)

    Returns:
        200 and a json object --
        {
            'msg': 'Project deleted successfully'
        }
    """
    project = maybe_get_project(project_id)  # check privilege and get project
    # Delete the whole image directory
    shutil.rmtree(
        os.path.join(app.config['STATIC_STORAGE_DIR'], str(project.id)))
    db.session.delete(project)
    db.session.commit()

    return construct_msg('Project deleted successfully'), 200


@bp.route('/project/<project_id>/users', methods=['GET'])
@jwt_required
def list_users_of_project(project_id):
    """
    List all the users having access to the specified project. Doesn't require
    a body
    Args:
        project_id -- The id of the project

    Raises:
        401 if
          * The project doesn't exist
          * Currently logged in user is not admin of this project (read write
            access)

    Returns:
        200 and a list of json objects. Example:
        ```
        [
            {
                "access_type": "AccessTypeEnum.READ_WRITE",
                "user": {
                    "username": "user0",
                    "email": "test@example.com",
                    "created_at": "2019-04-02 01:38:57.017910",
                    "privileges": "PrivilegesEnum.ADMIN"
                }
            }
        ]
        ```
    """
    project = maybe_get_project(project_id)  # check privilege and get project
    users = []
    for permission in project.permissions:
        users.append({
            'access_type': str(permission.access_type),
            'user': {
                'username': permission.user.username,
                'email': permission.user.email,
                'created_at': str(permission.user.created_at),
                'privileges': str(permission.user.privileges)
            }
        })
    return jsonify(users), 200
