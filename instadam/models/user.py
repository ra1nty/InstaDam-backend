import datetime as dt
import enum

from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from ..app import db


class PrivilegesEnum(enum.Enum):
    """Class PrivilegesEnum is an enum structure to represent the 
    permission level of a user

    Has two possible values: ADMIN and ANNOTATOR
    Return string values
    """

    ADMIN = 'admin'
    ANNOTATOR = 'annotator'


class User(db.Model):
    """Class User is a database model to represent a user

    Specifies the full database schema of the table 'user'

    Attributes:
        id: unique integer id given to a user (primary key)
        username: unique string that user chooses
        email: unique string (email address) that user specifies
        password: secure string that is greater than 8 chars in length, 
                    at least one uppercase char and one digit
        created_at: datetime that specifies when user signed up
        updated_at: datetime that specifies 
        privileges: enum type that specifies permission level of user
    """

    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128))
    created_at = db.Column(
        db.DateTime, nullable=False, default=dt.datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=dt.datetime.utcnow)
    privileges = db.Column(
        db.Enum(PrivilegesEnum),
        nullable=False,
        default=PrivilegesEnum.ANNOTATOR)

    project_permissions = relationship('ProjectPermission',
                                       back_populates='user')
    annotations = relationship('Annotation', backref='created_by')

    def set_password(self, password):
        """
        Set password to a hashed password
        """
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User %r>' % self.username
