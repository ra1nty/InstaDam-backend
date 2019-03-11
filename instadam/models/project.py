import datetime as dt

from sqlalchemy import Table, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship

from ..app import db

label_project_association_table = Table('label_project_association',
                                        db.Model.metadata,
                                        db.Column('label_id', db.Integer, db.ForeignKey('label.id')),
                                        db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
                                        UniqueConstraint('project_id', 'label_id'),
                                        )

class Project(db.Model):
    """Class Project is a database model to represent a project

    Specifies the full database schema of the table 'projects'

    Attributes:
        id: unique integer id given to a user (primary key)
        project_name: unique string that represents name of the project
        created_by: integer to represent id of user who created project
        created_at: datetime to represent date at which project was created
    """

    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(64), unique=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=dt.datetime.utcnow)

    images = relationship('Image', backref='project')
    permissions = relationship('ProjectPermission', back_populates='project')

    labels = relationship("Label", secondary=label_project_association_table, backref="projects")

    def __repr__(self):
        return '<Project: %r>' % self.project_name
