import datetime as dt
from werkzeug.security import check_password_hash, generate_password_hash
from ..app import db

class Project(db.Model):
	__tablename__ = 'projects'
	id = db.Column(db.Integer, primary_key=True)
	project_name = db.Column(db.String(64), unique=True, nullable=False)
	created_by = db.Column(db.Integer, nullable=False)
	created_at = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

	def __repr__(self):
		return '<Project %r>' % self.project_name