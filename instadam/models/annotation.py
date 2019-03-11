import datetime as dt
from ..app import db


class Label(db.Model):
    """Class Annotation is a database model to represent a label

    Specifies the full database schema of the table 'annotation'

    Attributes:
        id: unique integer id given to a user (primary key)
        image_id: integer to represent id of image that this annotation belongs to
        project_id: integer to represent id of project that this annotation belongs to
        created_by: integer to represent id of user that creates this annotation
        label_id: integer to represent id of label that this annotation is for
        added_at: datetime that image was added to the project
        data: largebinary to represent the mask (largebinary corresponds to BYTEA on PostgreSQL:
            see https://docs.sqlalchemy.org/en/latest/core/type_basics.html#sqlalchemy.types.LargeBinary)
    """

    __tablename__ = 'annotation'
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), nullable=False)
    # Since in image model, project_id is nullable, it is illogical to make the annotation non-nullable here
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    label_id = db.Column(db.Integer, db.ForeignKey('label.id'), nullable=False)
    added_at = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    data = db.Column(db.LargeBinary, nullable=False)

    def __repr__(self):
        return '<Annotation: for %r>' % self.image_id