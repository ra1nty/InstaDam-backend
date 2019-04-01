"""Helper function and modules
"""

from flask import abort, jsonify


def construct_msg(body):
    """Construct a json message.

    Args:
        body (Any): The body of the message.

    Returns:
        Response: Json response with the message.
    """

    return jsonify({'msg': str(body)})


def check_json(json, keys):
    for key in keys:
        if key not in json:
            abort(401, 'Missing key %s in json' % key)
