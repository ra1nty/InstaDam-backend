import datetime as dt
from ..app import db


class Annotation(db.Model):
    """Class Annotation is a database model to represent an annotation

    Specifies the full database schema of the table 'annotation'

    Attributes:
        id: unique integer id given to a user (primary key)
        project_id: integer to represent id of project that this annotation belongs to
        image_id: integer to represent id of image that this annotation belongs to
        creator_id: integer to represent id of user that creates this annotation
        label_id: integer to represent id of label that this annotation is for
        added_at: datetime that image was added to the project
        data: largebinary to represent the mask (largebinary corresponds to BYTEA on PostgreSQL:
            see https://docs.sqlalchemy.org/en/latest/core/type_basics.html#sqlalchemy.types.LargeBinary)
    """

    __tablename__ = 'annotation'
    id = db.Column(db.Integer, primary_key=True)

    # TODO: consistency problem - image's project and project_id should be the consistent
    # backref: original_image
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))

    # Since in image model, project_id is nullable, it is illogical to make it non-nullable here
    # backref: project
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    # backref: created_by
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # backref: label
    label_id = db.Column(db.Integer, db.ForeignKey('label.id'))

    added_at = db.Column(
        db.DateTime, nullable=False, default=dt.datetime.utcnow)
    data = db.Column(db.LargeBinary, nullable=False)
    vector = db.Column(db.LargeBinary, nullable=False)

    def __repr__(self):
        return '<Annotation: for %r>' % self.image_id
