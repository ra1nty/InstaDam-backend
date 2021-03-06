from ..app import db


class RevokedToken(db.Model):
    __tablename__ = 'invoken_token'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(128), unique=True, nullable=False)

    def __repr__(self):
        return self.jti
