"""
Module for handlers to convert error message to json response
"""

from flask import Blueprint, jsonify

bp = Blueprint('error', __name__, url_prefix='')


def register_error_handler(status_code):
    @bp.app_errorhandler(status_code)
    def handler(error):
        return jsonify({'msg': error.description}), status_code


register_error_handler(400)
register_error_handler(401)
register_error_handler(403)
register_error_handler(404)
register_error_handler(405)
register_error_handler(406)
register_error_handler(415)
