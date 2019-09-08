from flask import jsonify, request
import mysql.connector
from flask import Blueprint
from twilio.rest import Client
from geolocation import *
person  = Blueprint('person', __name__)

def get_file_contents(filename):
    """ Given a filename,
        return the contents of that file
    """
    try:
        with open(filename, 'r') as f:
            # It's assumed our file contains a single line,
            # with our API key
            return f.read().strip()
    except FileNotFoundError:
        print("'%s' file not found" % filename)





@person.route('/')
def index():
    return '/'



@person.route('/createPerson', methods=['GET', 'POST'])
def createNewPerson():
    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')
    uuid = request.args.get('uuid')
    school = request.args.get('school')

    try:
        queryInsert = 'Insert Into People(UUID, usualSchool) values (%s, %s);'
        cursor = cnx.cursor()
        cursor.execute(queryInsert, (uuid, school))
        cnx.commit()

        query = """
            Select id 
            From People 
            Where People.UUID = %s %s 
        """
        cursor = cnx.cursor()
        cursor.execute(query, (uuid, ""))
        result = cursor.fetchall()
        return jsonify(result)



    except Exception as e:
        print(e)
        return jsonify({"passed": False, "error": str(e)})



@person.route('/getLatLong')
def getLatLong():
    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')
    id = request.args.get('pid')
    query = """
        Select currentLatitude, currentLongitude 
        From People 
        Where People.id = %s %s 
    """
    cursor = cnx.cursor()
    cursor.execute(query, (id, ""))
    result = cursor.fetchall()
    return jsonify({'latitude': result[0][0], 'longitude': result[0][1]})



@person.route('/getLatLongAll')
def getLatLongAll():
    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')
    schoolName = request.args.get('schoolName')
    query = """
        Select id, currentLatitude, currentLongitude 
        From People 
        Where People.usualSchool = %s %s
    """
    cursor = cnx.cursor()
    cursor.execute(query, (schoolName, ""))
    result = cursor.fetchall()

    retList = []

    for res in result:
        retList.append( {'pid': res[0], 'latitude': res[1], 'longitude': res[2]})

    return jsonify(retList)

@person.route('/getAllPeople')
def getAllPeople():
    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')
    schoolName = request.args.get('schoolName')
    query = """
        Select id, phoneNumber, fullName, currentLatitude, currentLongitude 
        From People 
        Where People.usualSchool = %s %s and fullName is not NULL
    """
    cursor = cnx.cursor()
    cursor.execute(query, ("UIUC", ""))
    result = cursor.fetchall()

    retList = []

    for res in result:
        retList.append( {'pid': res[0], 'phoneNumber': res[1], 'fullName': res[2], 'latitude': res[3], 'longitude': res[4]})

    return jsonify(retList)


@person.route('/updateLocationPerson', methods=['GET', 'POST'])
def updateLocationPerson():
    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')
    pid = request.args.get('pid')
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    tupleTile = deg_to_tile(float(latitude), float(longitude), 18 )
    geolocationX = tupleTile[0]
    geolocationY = tupleTile[1]

    queryLatitude = """ Update People Set People.currentLatitude = %s Where People.id = %s;"""
    queryLongitude = """ Update People Set People.currentLongitude = %s Where People.id = %s;"""
    queryTileX = """ Update People Set People.xTile = %s Where People.id = %s;"""
    queryTileY = """ Update People Set People.yTile = %s Where People.id = %s;"""

    cursor = cnx.cursor()
    cursor.execute(queryLatitude, (latitude, pid))
    cursor.execute(queryLongitude, (longitude, pid))
    cursor.execute(queryTileX, (geolocationX, pid))
    cursor.execute(queryTileY, (geolocationY, pid))
    cnx.commit()

    return "0"




@person.route('/getAdminPhoneNums')
def getJSONAdminNums():
    return jsonify(getAdminPhoneNums);

def getAdminPhoneNums():
    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')
    id = request.args.get('pid')
    query = """
        Select * from Admins; 
    """



    cursor = cnx.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    return result


@person.route('/sendPersonCheckin')
def sendPersonCheckin():
    phoneNumber = request.args.get('phoneNumber')
    sid = get_file_contents('sid.txt')
    authToken = get_file_contents('TwilioAuth.txt')
    client = Client(
        sid,
        authToken
    )

    mes = client.messages.create(
        to= str(phoneNumber),
        from_ = '15087318632',
        body = "This is a checkin text from an administrator asking you to send a message about your status"

    )

    return ('', 204)


@person.route('/getPeopleByTileGrouping')
def getPeopleByTileGrouping():
    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')

    buildingId = request.args.get('buildingId')
    query = """
                Select People.xTile, People.yTile, People.id, People.currentLatitude, People.currentLongitude 
                From (Select distinct buildingID, buildingStatus, GeoFeatures.schoolName, xTile, yTile, structureType  
                        from ProtocolStatusCurrent  
                            Join GeoFeatures  
                            on ProtocolStatusCurrent.buildingID = GeoFeatures.idBuilding  
                            and ProtocolStatusCurrent.schoolName = GeoFeatures.schoolName ) as BuildingTileInformation, 
                    People 
                Where People.xTile = BuildingTileInformation.xTile and People.yTile = BuildingTileInformation.yTile 
                Order By People.xTile, People.yTile; 
                    """
    cursor = cnx.cursor()
    cursor.execute(query)
    result = cursor.fetchall()

    return jsonify(result)