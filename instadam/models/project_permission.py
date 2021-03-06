import enum

from sqlalchemy.orm import relationship

from ..app import db


class AccessTypeEnum(enum.Enum):
    """Class AccessTypeEnum is an enum structure to represent the access 
    type of a specific user for a specific project

    Has two possible values: READ_WRITE (given to admin) 
    and READ_ONLY (given to annotators)
    Return string values
    """

    READ_WRITE = 'rw'
    READ_ONLY = 'r'


class ProjectPermission(db.Model):
    """Class User is a database model to represent a project permission

    Specifies the full database schema of the table 'project_permissions'
    Used to determine which user has access to which project and what 
    kind of access this entails

    Attributes:
        id: unique integer id given to a permission entry (primary key)
        project_id: integer project id of permission entry
        user_id: integer user id that has access to project with project_id
        access_type: enum type that specifies the level of access
    """

    __tablename__ = 'project_permission'
    id = db.Column(db.Integer, primary_key=True)
    access_type = db.Column(db.Enum(AccessTypeEnum), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    user = relationship('User', back_populates='project_permissions')
    project = relationship('Project', back_populates='permissions')

    def __repr__(self):
        return '<Access type of permission: %r>' % self.access_type
