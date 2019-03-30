"""Utilities related to uploading and serving files.
"""
import os

from flask import abort
from flask import current_app as app


def parse_and_validate_file_extension(file_name, valid_extensions):
    """Parse and validate the file name has a valid image extension.

    Args:
        file_name (str): File name
        valid_extensions(set): Extensions for this file type

    Returns:
        str: File extension
    """

    split = file_name.lower().split('.')
    if split and split[-1] in valid_extensions:
        return split[-1]
    abort(415, 'Invalid file extension for %s' % file_name)


def get_project_dir(project):
    """
    Return the path to the project directory. And create one if doesn't exist.
    Args:
        project: Project

    Returns:
        Path
    """
    project_dir = os.path.join(app.config['STATIC_STORAGE_DIR'],
                               str(project.id))
    if not os.path.exists(project_dir):
        os.mkdir(project_dir)
    return project_dir


def get_project_static_url(project):
    """
    Return the url path to the static file directory
    Args:
        project: The project

    Returns:
        Path

    """
    return os.path.join(app.config['STATIC_STORAGE_URL'],
                        str(project.id))
