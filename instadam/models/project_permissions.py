import enum
import datetime as dt
from ..app import db

class AccessTypeEnum(enum.Enum):
    READ_WRITE = 'rw'
    READ_ONLY = 'r'

class ProjectPermissions(db.Model):
    __tablename__ = 'project_permissions'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    access_type = db.Column(db.Enum(AccessTypeEnum), nullable=False)