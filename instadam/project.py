
from flask import Blueprint, jsonify, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError, DatabaseError

from instadam.models.project_permission import AccessTypeEnum, ProjectPermission
from instadam.models.user import User, PrivilegesEnum
from .app import db
from .models.project import Project
from .utils import construct_msg


bp = Blueprint('project', __name__, url_prefix='')

"""
Some note: 
1. project name must be provided
2. must be signed in. check user_id (created_by) from token
3. add permission RW to creator
"""


@bp.route('/project', methods=['POST'])
# @jwt_required
def create_project():
    """ Create a new project by the user currently signed in

    Create a new project entry in the database and a new folder in the filesystem
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

    identity = get_jwt_identity()
    user = User.query.filter_by(username=identity).first()

    if user.privileges != PrivilegesEnum.ADMIN:
        abort(401, 'User is not Admin')

    project_name = req['project_name']
    created_by = user.id

    project = Project(project_name=project_name, created_by=created_by)
    try:
        db.session.add(project)
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        abort(400, 'Duplicate project name. '
                   'Please provide a different project name.')
    else:
        access_type = AccessTypeEnum.READ_WRITE
        user_id = user.id
        project_id = project.id
        project_permission = ProjectPermission(access_type=access_type,
                                               user_id=user_id,
                                               project_id=project_id)
        try:
            db.session.add(project_permission)
            db.session.flush()
        except DatabaseError:
            db.session.rollback()
            abort(400, 'Cannot update project permission for user.')

    db.session.commit()
    return jsonify({'project_id': project.id}), 201
