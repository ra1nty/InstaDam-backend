"""Module for creating app to run with wsgi
"""

from instadam.app import create_app

app = create_app('production')

if __name__ == '__main__':
    app.run()
