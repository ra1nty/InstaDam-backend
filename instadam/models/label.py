from sqlalchemy.orm import relationship

from ..app import db


class Label(db.Model):
    """Class label is a database model to represent an label

    Specifies the full database schema of the table 'label'

    Attributes:
        id: unique integer id given to a user (primary key)
        label_name: integer to represent id of label that this annotation is for
    """

    __tablename__ = 'label'
    id = db.Column(db.Integer, primary_key=True)
    label_name = db.Column(db.String(64), nullable=False)
    label_color = db.Column(db.String(7), default="#E84A27")
    # backref: project
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    annotations = relationship("Annotation", backref="label")

    def __repr__(self):
        return '<Label %r>' % self.label_name
