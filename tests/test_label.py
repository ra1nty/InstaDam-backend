from instadam.models.label import Label


def test_label_repr(client):
    label = Label(label_name='test label')
    assert str(label) == '<Label %r>' % 'test label'
