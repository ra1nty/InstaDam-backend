"""Module for creating app to run with wsgi
"""
from instadam.app import create_app, db

app = create_app('production')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
