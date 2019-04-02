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
    """
    Check whether the json in request has required keys
    Args:
        json: The json object
        keys: The keys to check

    Returns:
        400 if there are some missing key
        None if OK.
    """
    if json is None:
        abort(400, 'No Json object provided')
    for key in keys:
        if key not in json:
            abort(400, 'Missing key %s in json' % key)
