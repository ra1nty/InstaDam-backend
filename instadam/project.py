
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from .app import db
from .models.project import Project
from .utils import construct_msg
from .utils.exception import MsgException

bp = Blueprint('project', __name__, url_prefix='')





"""
project name, creator name
"""
@bp.route('/project', methods=['POST'])
def create_project():
    """ Create project endpoint for application

    Take POST json data 

    Returns: 
    """

    req = request.get_json()

    if 'project_name' not in req:
        return construct_msg("Project name must be specified."), 400
    if 'created_by' not in req:
        return construct_msg("Creator name must be specified."), 400


    project_name = req['project_name']
    created_by = req['created_by']

    project = Project(project_name=project_name, created_by=created_by)
    try:
        db.session.add(project)
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        return construct_msg('Project %s already exist' % project_name), 401
    else:
        db.session.commit()

    return jsonify({'created_by' : project.created_by, 'created_at' : project.created_at, 'project_id' : project.id}), 201
