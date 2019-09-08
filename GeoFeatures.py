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
                    Select idBuilding, latitude, longitude, xTile, yTile from GeoFeatures where idBuilding = %s %s Order By created_at;
                    """
    cursor = cnx.cursor()
    cursor.execute(query, (buildingId, ""))
    result = cursor.fetchall()
    retList = []
    for res in result:
        retList.append( {'buildingId': res[0], 'latitude': res[1], 'longitude': res[2], "xTile": res[3], "yTile": res[4]})

    return jsonify(retList)



def getAllBuildings(buildingIdList):
    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')

    allItems = []
    for bid in buildingIdList:
        buildingId = bid
        query = """
                        Select idBuilding, latitude, longitude, xTile, yTile from GeoFeatures where idBuilding = %s %s and schoolName = "UIUC" Order By created_at;
                        """
        cursor = cnx.cursor()
        cursor.execute(query, (buildingId, ""))
        result = cursor.fetchall()
        retList = []
        for res in result:
            retList.append( {'buildingId': res[0], 'latitude': res[1], 'longitude': res[2], "xTile": res[3], "yTile": res[4]})
        allItems.append(retList)
    return jsonify(allItems)


def getAllBuildings():
    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')

    allItems = []

    query = """
                        Select idBuilding, latitude, longitude, xTile, yTile from GeoFeatures where schoolName = "UIUC" Order By created_at;
                        """
    cursor = cnx.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    retList = []
    for res in result:
        retList.append( {'buildingId': res[0], 'latitude': res[1], 'longitude': res[2], "xTile": res[3], "yTile": res[4]})
        
    return retList






@geo_features.route('/getActiveBuildings')
def getActiveBuildings():
    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')

    allItems = []

    query = """
                        Select distinct ProtocolStatusCurrent.buildingId, latitude, longitude,  buildingStatus from ProtocolStatusCurrent join GeoFeatures on ProtocolStatusCurrent.buildingID = GeoFeatures.idBuilding;
                        """
    cursor = cnx.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    retList = []
    for res in result:
        retList.append(
            {'buildingId': res[0], 'latitude': res[1], 'longitude': res[2], "color": res[3]})

    return jsonify(retList)