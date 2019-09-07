from flask import jsonify, request
import mysql.connector
from flask import Blueprint
from Person import get_file_contents

message_board  = Blueprint('message_board', __name__)