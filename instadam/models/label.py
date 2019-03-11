import datetime as dt
from ..app import db


class Label(db.Model):
    """Class label is a database model to represent an label

    Specifies the full database schema of the table 'label'

    Attributes:
        id: unique integer id given to a user (primary key)
        label_name: integer to represent id of label that this annotation is for
    """

    __tablename__ = 'annotation'
    id = db.Column(db.Integer, primary_key=True)
    label_name = db.Column(db.String(64), nullable=False)

    annotation_id = db.Column(db.Integer, db.ForeignKey('annotation.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    def __repr__(self):
        return '<Annotation: for %r>' % self.image_id
