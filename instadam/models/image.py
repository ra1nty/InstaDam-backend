import datetime as dt
import os
import uuid

from flask import abort
from flask import current_app as app
from sqlalchemy.orm import relationship

from instadam.models.project import Project
from instadam.utils.file import (get_project_dir, get_project_static_url,
                                 parse_and_validate_file_extension)
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
    image_url = db.Column(db.String(256))
    image_storage_path = db.Column(db.String(256))
    modified_at = db.Column(
        db.DateTime, nullable=False, default=dt.datetime.utcnow)
    is_annotated = db.Column(db.Boolean, nullable=False, default=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'),
                           nullable=False)

    annotations = relationship('Annotation', backref='original_image',
                               order_by='Annotation.label_id')

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
        project_dir = get_project_dir(project)
        new_file_name = '%s.%s' % (str(uuid.uuid4()), extension)
        self.image_name = img_file.filename
        self.image_storage_path = os.path.join(project_dir, new_file_name)
        self.image_url = os.path.join(get_project_static_url(project),
                                      new_file_name)
        img_file.save(self.image_storage_path)

    def save_empty_image(self, original_file_name):
        extension = parse_and_validate_file_extension(original_file_name,
                                                      VALID_IMG_EXTENSIONS)
        project = Project.query.filter_by(id=self.project_id).first()
        project_dir = os.path.join(app.config['STATIC_STORAGE_DIR'],
                                   str(project.id))
        if not os.path.exists(project_dir):
            os.mkdir(project_dir)
        project_url = get_project_static_url(project)
        new_file_name = '%s.%s' % (str(uuid.uuid4()), extension)
        self.image_name = original_file_name
        self.image_url = os.path.join(project_url, new_file_name)
        self.image_storage_path = os.path.join(project_dir, new_file_name)

    def __repr__(self):
        return '<Image: %r>' % self.image_name
