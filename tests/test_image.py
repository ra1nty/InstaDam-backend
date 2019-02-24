from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import HTTPException

from instadam.app import create_app, db
from instadam.models.image import Image
from tests.conftest import TEST_MODE


def test_image_repr(client):
    image = Image(image_name='cracked_building.png')
    assert str(image) == '<Image: %r>' % 'cracked_building.png'


def test_invalid_project():
    app = create_app(TEST_MODE)
    with app.app_context():
        db.create_all()
        with open('tests/cat.jpg', 'rb') as fd:
            img = FileStorage(fd)
            image = Image(project_id=0)
            try:
                image.save_image_to_project(img)
                assert False
            except HTTPException as exception:
                assert 400 == exception.code
