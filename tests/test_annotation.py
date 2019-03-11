from instadam.models.annotation import Annotation
import os


def test_annotation_repr():
    data = os.urandom(35000)
    annotation = Annotation(image_id=1, data=data)
    assert str(annotation) == '<Annotation: for %r>' % 1
