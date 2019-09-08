from flask import jsonify, request
import mysql.connector
from flask import Blueprint
from Person import get_file_contents

geo_features  = Blueprint('geo_features', __name__)


@geo_features.route('/')
def index():
    return '/'

@geo_features.route('/getSingleBuilding')
def getSingleBuilding():
    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')

    buildingId = request.args.get('buildingId')
    query = """
                    Select idBuilding, latitude, longitude from GeoFeatures where idBuilding = %s %s Order By created_at;
                    """
    cursor = cnx.cursor()
    cursor.execute(query, (buildingId, ""))
    result = cursor.fetchall()
    retList = []
    for res in result:
        retList.append( {'buildingId': res[0], 'latitude': res[1], 'longitude': res[2]})

    return jsonify(retList)

# @geo_features.route('/create')