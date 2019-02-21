import datetime as dt
from ..app import db


class Image(db.Model):
    """Class User is a database model to represent a user

    Specifies the full database schema of the table 'user'

    Attributes:
        id: unique integer id given to a user (primary key)
        project_id: integer to represent id of project that this image belongs to
        image_name: string to represent name of image
        added_at: datetime that image was added to the project
    """

    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer, db.ForeignKey('project.id'), nullable=False)
    image_name = db.Column(db.String(64), nullable=False)
    added_at = db.Column(
        db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __repr__(self):
        return '<Image: %r>' % self.image_name