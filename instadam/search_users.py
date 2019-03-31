"""Module related to searching for users
"""
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import (jwt_required)
from instadam.app import db
from sqlalchemy.exc import IntegrityError

bp = Blueprint('project', __name__, url_prefix='/users')
