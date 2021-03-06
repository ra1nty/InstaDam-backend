"""Module related to testing correctness of relationships between model schemas
"""

from instadam.models.annotation import Annotation
from instadam.models.image import Image
from instadam.models.label import Label
from instadam.models.message import Message
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


def test_label_and_project(client):
    label = Label()
    label1 = Label()
    project = Project()

    project.labels.append(label)
    project.labels.append(label1)
    assert (len(project.labels) == 2)
    assert (label.project_id == project.id)
    assert (label1.project_id == project.id)


# TODO: test label_project_association unique (cannot add the same association twice)


def test_annotation_and_image(client):
    annotation = Annotation()
    image = Image()
    image.annotations.append(annotation)
    assert len(image.annotations) == 1
    assert annotation == image.annotations[0]
    assert image == annotation.original_image

    annotation1 = Annotation()
    image.annotations.append(annotation1)
    assert len(image.annotations) == 2
    assert annotation1 == image.annotations[1]
    assert image == annotation1.original_image


def test_annotation_and_project(client):
    annotation = Annotation()
    annotation1 = Annotation()
    project = Project()
    project.annotations.append(annotation)
    project.annotations.append(annotation1)

    assert annotation == project.annotations[0]
    assert project == annotation.project

    assert len(project.annotations) == 2
    assert annotation1 == project.annotations[1]
    assert project == annotation1.project


def test_annotation_and_user(client):
    annotation = Annotation()
    annotation1 = Annotation()
    user = User()
    user.annotations.append(annotation)
    user.annotations.append(annotation1)

    assert annotation == user.annotations[0]
    assert user == annotation.created_by

    assert len(user.annotations) == 2
    assert annotation1 == user.annotations[1]
    assert user == annotation1.created_by


def test_message_and_user(client):
    message1 = Message()
    sender1 = User()
    receiver_a = User()
    receiver_b = User()

    sender1.sent_messages.append(message1)
    receiver_a.received_messages.append(message1)
    receiver_b.received_messages.append(message1)

    assert message1 == sender1.sent_messages[0]
    assert sender1 == message1.sender

    assert message1 == receiver_a.received_messages[0]
    assert message1 == receiver_b.received_messages[0]
    assert receiver_a == message1.receivers[0]
    assert receiver_b == message1.receivers[1]

    # Second sender
    message2 = Message()
    sender2 = User()

    sender2.sent_messages.append(message2)
    receiver_a.received_messages.append(message2)

    assert message2 == sender2.sent_messages[0]
    assert sender2 == message2.sender

    assert message2 == receiver_a.received_messages[1]
    assert receiver_a == message2.receivers[0]