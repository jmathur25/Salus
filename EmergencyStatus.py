from flask import jsonify, request
import mysql.connector
from flask import Blueprint
from Person import get_file_contents

emergency_status  = Blueprint('emergency_status', __name__)


@emergency_status.route('/')
def index():
    return '/'


@emergency_status.route('/getInitialBuildings')
def getLatLong():
    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')
    # id = request.args.get('pid')

    query = """
        Select protocolID, ProtocolSynthesis.buildingID, latitude, longitude, schoolName, updated_at, created_at 
        From ( 
		    Select * 
            From ProtocolToBuilding 
            Where ProtocolToBuilding.protocolID = 1 
            ) as ProtocolSynthesis Join GeoFeatures  
        on buildingID = GeoFeatures.idBuilding AND schoolName = "UIUC" 
        order by created_at;  
    """

    cursor = cnx.cursor()
    cursor.execute(query)
    result = cursor.fetchall()

    buildingPoints = []
    for res in result:
        buildingPoints.append({"protocolID": res[0], "buildingID": res[1], "latitude": res[2], "longitude": res[3], "schoolName": res[4]})
    return jsonify(buildingPoints)