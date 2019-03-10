import datetime as dt
import os
import uuid

from flask import abort
from flask import current_app as app

from instadam.models.project import Project
from instadam.utils.file import parse_and_validate_file_extension
from ..app import db

VALID_IMG_EXTENSIONS = {'png', 'jpg', 'jpeg'}


class Image(db.Model):
    """Class User is a database model to represent a user

    Specifies the full database schema of the table 'user'

    Attributes:
        id: unique integer id given to a user (primary key)
        project_id: integer to represent id of project that this image
        belongs to
        image_name: string to represent name of image
        added_at: datetime that image was added to the project
    """

    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(64), nullable=False)
    image_path = db.Column(db.String(256))
    added_at = db.Column(
        db.DateTime, nullable=False, default=dt.datetime.utcnow)
    is_annotated = db.Column(db.Boolean, nullable=False, default=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    def save_image_to_project(self, img_file):
        """Saves the image file associated to disk.

        Args:
            img_file: Image file get from the request.
        """

        extension = parse_and_validate_file_extension(img_file.filename,
                                                      VALID_IMG_EXTENSIONS)
        project = Project.query.filter_by(id=self.project_id).first()
        if project is None:
            abort(400, 'Project with id %d does not exist.' % self.project_id)
        project_dir = os.path.join(app.config['STATIC_STORAGE_DIR'],
                                   str(project.id))
        if not os.path.exists(project_dir):
            os.mkdir(project_dir)
        new_file_name = '%s.%s' % (str(uuid.uuid4()), extension)
        self.image_name = new_file_name
        img_file.save(os.path.join(project_dir, new_file_name))

    def save_empty_image(self, original_file_name):
        extension = parse_and_validate_file_extension(original_file_name,
                                                      VALID_IMG_EXTENSIONS)
        project = Project.query.filter_by(id=self.project_id).first()
        project_dir = os.path.join(app.config['STATIC_STORAGE_DIR'],
                                   str(project.id))
        if not os.path.exists(project_dir):
            os.mkdir(project_dir)
        new_file_name = '%s.%s' % (str(uuid.uuid4()), extension)
        self.image_name = new_file_name

    def __repr__(self):
        return '<Image: %r>' % self.image_name
