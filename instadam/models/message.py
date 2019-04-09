import datetime as dt
import enum

from sqlalchemy.orm import relationship
from ..app import db


class MessageTypeEnum(enum.Enum):
    READ_WRITE_PERMISSION_REQUEST = 'rw_request'
    READ_ONLY_PERMISSION_REQUEST = 'r_request'


class Message(db.Model):
    """Class Project is a database model to represent a project

    Specifies the full database schema of the table 'projects'

    Attributes:
        id: unique integer id given to a user (primary key)
        project_name: unique string that represents name of the project
        created_by: integer to represent id of user who created project
        created_at: datetime to represent date at which project was created
    """

    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)

    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender = relationship("User", back_populates="sent_messages")
    receivers = relationship(
        "User",
        secondary="message_receiver_link",
        back_populates="received_messages")

    # maybe in the future
    type = db.Column(db.Enum(MessageTypeEnum), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=dt.datetime.utcnow)

    fulfilled = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Project: %r>' % self.project_name


class MessageReceiverLink(db.Model):
    __tablename__ = 'message_receiver_link'
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), primary_key=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

