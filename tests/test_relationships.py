from instadam.models.image import Image
from instadam.models.project import Project
from instadam.models.project_permission import ProjectPermission
from instadam.models.user import User


def test_user_and_project(client):
    user = User()
    project = Project()
    project_permission = ProjectPermission()

    user.project_permissions.append(project_permission)
    project_permission.project = project

    assert len(user.project_permissions) == 1
    assert len(project.permissions) == 1
    assert project_permission == user.project_permissions[0]
    assert project_permission == project.permissions[0]
    assert user == project_permission.user
    assert project == project_permission.project


def test_image_and_project(client):
    image = Image()
    project = Project()

    project.images.append(image)
    assert len(project.images) == 1
    assert image == project.images[0]
    assert project == image.project
