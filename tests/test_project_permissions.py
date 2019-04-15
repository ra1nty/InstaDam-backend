"""Module related to testing project permission model
"""

from instadam.models.project_permission import ProjectPermission
from instadam.models.project_permission import AccessTypeEnum


def test_project_permissions_repr(client):
    project_permissions = ProjectPermission(
        access_type=AccessTypeEnum.READ_ONLY)
    assert str(project_permissions
              ) == '<Access type of permission: %r>' % AccessTypeEnum.READ_ONLY
