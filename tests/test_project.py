from instadam.models.project import Project


def test_project_repr(client):
    project = Project(project_name='buildings_project')
    assert str(project) == '<Project: %r>' % 'buildings_project'
