from instadam.models.project import Project


def test_project_repr(client):
    project = Project(project_name='buildings_project')
    assert str(project) == '<Project: %r>' % 'buildings_project'


def create_project(client, project_name, created_by):
    return client.post(
        '/project',
        json={
            'project_name': project_name,
            'created_by': created_by
        },
        follow_redirects=True)


project1 = 'project1'
creator1 = 'lita'
project2 = 'project2'
creator2 = 'susan'


def test_create_project(client):
    rv = create_project(client, 'project1', 'lita')
    code = rv.status
    json_data = rv.get_json()
    print(json_data)
    assert code == '201 CREATED'
    assert 'project' in json_data
    assert json_data['project'] == project1
    assert 'created_by' in json_data
    assert json_data['created_by'] == creator1

    rv = create_project(client, project1, creator2)
    code = rv.status
    assert code == '401 UNAUTHORIZED'
