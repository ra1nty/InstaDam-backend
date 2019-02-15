"""Helper function and modules
"""

from flask import jsonify


def construct_msg(body):
    """Construct a json message.

    Args:
        body (Any): The body of the message.

    Returns:
        Response: Json response with the message.
    """

    return jsonify({'msg': str(body)})
