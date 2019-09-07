from flask import jsonify, request
import mysql.connector
from flask import Blueprint
from Person import get_file_contents

emergency_status  = Blueprint('emergency_status', __name__)


@emergency_status.route('/')
def index():
    return '/'


def getQueryBuildingInit():
    query = """
            Select protocolID, ProtocolSynthesis.buildingID, latitude, longitude, schoolName, buildingStatus, updated_at, created_at 
            From (
                    Select ProtocolToBuilding.protocolID, ProtocolStatusInitial.buildingID, buildingStatus 
                    From ProtocolToBuilding, ProtocolStatusInitial 
                    Where ProtocolToBuilding.protocolID = %s and ProtocolStatusInitial.buildingID = ProtocolToBuilding.buildingID 
                 ) as ProtocolSynthesis Join GeoFeatures  
            on buildingID = GeoFeatures.idBuilding AND schoolName = %s
            order by created_at;  
    """

    return query


@emergency_status.route('/getInitialBuildings')
def getInitialBuildings():
    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')
    protocolID = request.args.get('protocolID')

    query = getQueryBuildingInit()

    cursor = cnx.cursor()
    cursor.execute(query, (protocolID, "UIUC"))
    result = cursor.fetchall()

    buildingPoints = []
    for res in result:
        buildingPoints.append({"protocolID": res[0], "buildingID": res[1], "latitude": res[2], "longitude": res[3], "schoolName": res[4], "buildingStatus": res[5]})

    return jsonify(buildingPoints)


@emergency_status.route('/startEmergency', methods=['GET', 'POST'])
def startEmergency():
    protocolID = request.args.get('protocolID')

    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')


    query = """
            Select Distinct ProtocolSynthesis.buildingID, buildingStatus
            From (
                    Select ProtocolToBuilding.protocolID, ProtocolStatusInitial.buildingID, buildingStatus 
                    From ProtocolToBuilding, ProtocolStatusInitial 
                    Where ProtocolToBuilding.protocolID = %s and ProtocolStatusInitial.buildingID = ProtocolToBuilding.buildingID 
                 ) as ProtocolSynthesis Join GeoFeatures  
            on buildingID = GeoFeatures.idBuilding AND schoolName = %s
            order by created_at;  
        """

    cursor = cnx.cursor()
    cursor.execute(query, (protocolID, "UIUC"))
    result = cursor.fetchall()


    for res in result:
        insertQuery = """
                        Insert Into ProtocolStatusCurrent(buildingID, buildingStatus, schoolName) values(%s, %s, %s)
                        """
        cursor = cnx.cursor()
        cursor.execute(insertQuery, (res[0], res[1], "UIUC"))
        cnx.commit()

    return jsonify(True)




@emergency_status.route('/endEmergency', methods=['GET', 'POST'])
def endEmergency():

    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')

    insertQuery = """
                    Delete From ProtocolStatusCurrent Where ProtocolStatusCurrent.schoolName = "UIUC"
                    """
    cursor = cnx.cursor()
    cursor.execute(insertQuery)
    cnx.commit()

    return jsonify(True)




@emergency_status.route('/addBuilding', methods=['GET', 'POST'])
def addBuilding():

    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')

    buildingId = request.args.get('buildingId')
    status = request.args.get('status')


    insertQuery = """
                    Insert Into ProtocolStatusCurrent(buildingID, buildingStatus, schoolName) values(%s, %s, %s);
                    """
    cursor = cnx.cursor()
    cursor.execute(insertQuery, (buildingId, status, "UIUC"))
    cnx.commit()

    return jsonify(True)


@emergency_status.route('/removeBuilding', methods=['GET', 'POST'])
def removeBuilding():

    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')

    buildingId = request.args.get('buildingId')


    insertQuery = """
                    Delete From ProtocolStatusCurrent Where ProtocolStatusCurrent.buildingID = %s AND ProtocolStatusCurrent.schoolName = %s
                    """
    cursor = cnx.cursor()
    cursor.execute(insertQuery, (buildingId, "UIUC"))
    cnx.commit()

    return jsonify(True)


@emergency_status.route('/changeStatus', methods=['GET', 'POST'])
def changeStatus():

    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')

    buildingId = request.args.get('buildingId')
    status = request.args.get('status')


    insertQuery = """
                    Update ProtocolStatusCurrent 
                    Set ProtocolStatusCurrent.buildingStatus = %s
                    Where ProtocolStatusCurrent.buildingID = %s AND ProtocolStatusCurrent.schoolName = %s
                    """
    cursor = cnx.cursor()
    cursor.execute(insertQuery, (status, buildingId, "UIUC"))
    cnx.commit()

    return jsonify(True)