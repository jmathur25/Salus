from flask import jsonify, request
import mysql.connector
from flask import Blueprint
from Person import get_file_contents

geo_features  = Blueprint('geo_features', __name__)


@geo_features.route('/')
def index():
    return '/'

