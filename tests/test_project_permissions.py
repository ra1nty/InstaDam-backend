from instadam.models.project_permissions import ProjectPermissions
from instadam.models.project_permissions import AccessTypeEnum


def test_project_permissions_repr(client):
    project_permissions = ProjectPermissions(
        access_type=AccessTypeEnum.READ_ONLY)
    assert str(project_permissions
              ) == '<Access type of permission: %r>' % AccessTypeEnum.READ_ONLY
