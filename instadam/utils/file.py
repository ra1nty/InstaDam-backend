"""Utilities related to uploading and serving files.
"""
from flask import abort


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
    abort(400, 'Invalid file extension for %s' % file_name)
