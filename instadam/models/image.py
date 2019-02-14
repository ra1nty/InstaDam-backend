import datetime as dt
from ..app import db

class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, nullable=False)
    image_name = db.Column(db.String(64), nullable=False)
    added_at = db.Column(db.Datetime, nullable=False, default=dt.datetime.utcnow)

    def __repr__(self):
        return '<Image: %r>' % self.image_name