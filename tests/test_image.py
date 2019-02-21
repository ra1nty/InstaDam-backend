from instadam.models.image import Image


def test_image_repr(client):
    image = Image(image_name='cracked_building.png')
    assert str(image) == '<Image: %r>' % 'cracked_building.png'