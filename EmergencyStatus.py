from flask import jsonify, request, render_template, redirect
import mysql.connector
from flask import Blueprint
from Person import get_file_contents
from twilio.rest import Client
import config_reader
import imagery
import json
emergency_status  = Blueprint('emergency_status', __name__)


@emergency_status.route('/')
def index(zoom=None, lat=None, lng=None):

    if lat is None or lng is None or zoom is None:
        config = config_reader.get_config()
        lat = config['start_lat']
        lng = config['start_lng']
        zoom = config['start_zoom']

    access_key = config_reader.get_config()['accessKey']
    context = {}
    context['lat'] = lat
    context['lng'] = lng
    context['zoom'] = zoom
    context['access_key'] = access_key
    jsonDoc = isActiveEmergency()
    print(jsonDoc)
    if jsonDoc:

        return render_template('Dashboard.html', **context)
    else:
        return render_template("NoEmergency.html")


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
    sendEmergencyInfoToTwilioSubs(protocolID)
    sendEmergencyPortalToAdmins(protocolID)
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

    return redirect("/emergency", code=302)



def sendEmergencyInfoToTwilioSubs(protocolID):

    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')


    query = """
            Select * 
            From Protocols
            Where id = %s %s;
        """

    cursor = cnx.cursor()
    cursor.execute(query, (protocolID, ""))
    result = cursor.fetchall()
    print(result)
    protocolName = result[0][2]
    protocolDesc = result[0][3]
    protocolType = result[0][4]


    query = """
            Select fullName, phoneNumber
            From People
            Where usualSchool = "UIUC" and phoneNumber is not Null
        """

    cursor = cnx.cursor()
    cursor.execute(query)
    result = cursor.fetchall()


    sid = get_file_contents('sid.txt')
    authToken = get_file_contents('TwilioAuth.txt')
    client = Client(
        sid,
        authToken
    )
    for res in result:
        print(res[1])
        mes = client.messages.create(
            to= str(res[1]),
            from_ = '15087318632',
            body = "IMPORTANT! There is an " + str(protocolType) + " We are following " + str(protocolName) + " which says to " + str(protocolDesc) + ""

        )

    pass


def sendEmergencyPortalToAdmins(protocolID):
    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')

    query = """
                Select * 
                From Protocols
                Where id = %s %s;
            """

    cursor = cnx.cursor()
    cursor.execute(query, (protocolID, ""))
    result = cursor.fetchall()
    print(result)
    protocolName = result[0][2]
    protocolDesc = result[0][3]
    protocolType = result[0][4]

    query = """
                Select phoneNumber
                From Admins
                Where phoneNumber is not Null
            """

    cursor = cnx.cursor()
    cursor.execute(query)
    result = cursor.fetchall()

    sid = get_file_contents('sid.txt')
    authToken = get_file_contents('TwilioAuth.txt')
    client = Client(
        sid,
        authToken
    )
    for res in result:
        print(res[0])
        mes = client.messages.create(
            to=str(res[0]),
            from_='15087318632',
            body="IMPORTANT! There is an " + str(protocolType) + " We are following " + str(
                protocolName) + " which says to " + str(protocolDesc) + " MANAGE PORTAL: http://salus.kxgp8z9g5d.us-east-2.elasticbeanstalk.com/emergency/"

        )

    pass


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

    return render_template("NoEmergency.html")




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



@emergency_status.route('/isActiveEmergency', methods=['GET'])
def isActiveEmergency():

    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')

    query = """
                    Select * from ProtocolStatusCurrent Where schoolName = %s %s;
                    """
    cursor = cnx.cursor()
    cursor.execute(query, ("UIUC", ""))
    result = cursor.fetchall()

    print(len(result))
    if len(result) > 0:
        return True



    return False


@emergency_status.route('/isActiveEmergencyiOS', methods=['GET'])
def isActiveEmergency():

    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')

    query = """
                    Select * from ProtocolStatusCurrent Where schoolName = %s %s;
                    """
    cursor = cnx.cursor()
    cursor.execute(query, ("UIUC", ""))
    result = cursor.fetchall()

    print(len(result))
    if len(result) > 0:
        return jsonify(True)



    return jsonify(False)



@emergency_status.route('/setup', methods=['POST'])
def setup():
    # from .setup import ...
    return "success"


@emergency_status.route('/setup/corners', methods=['POST'])
def identify_region():
    result = request.form
    info = result_to_dict(result)
    lat = float(info['lat'])
    lng = float(info['lng'])
    zoom = float(info['zoom'])

    imd = get_imd()
    # old way, tabling for now...
    # image = imd.get_image_from_latlng_outline((lat1, lng1), (lat2, lng2))
    # image.save('setup/setup_image.png')
    # image = np.array(image) # detection needs an np array

    # find xtile, ytile
    xtile, ytile = geolocation.deg_to_tile(lat, lng, zoom)
    image = np.array(imd.download_tile(xtile, ytile, zoom))

    # SETUP MRCNN STUFF
    global mrcnn
    if mrcnn is None:  # import if not already imported
        print('import MRCNN stuff...')
        from Mask_RCNN_Detect import Mask_RCNN_Detect
        mrcnn = Mask_RCNN_Detect('weights/epoch55.h5')

    mask_data = mrcnn.detect_building(image, lat, lng, zoom)
    building_ids = list(mask_data.keys())
    building_points = list(mask_data.values())

    json_post = {"rects_to_add": [{
        "ids": building_ids,
        "points": building_points
    }],
        "rects_to_delete": {"ids": []}
    }
    return json.dumps(json_post)


@emergency_status.route('/setup/delete', methods=['POST'])
def delete_building():
    result = request.form
    info = result_to_dict(result)
    lat = float(info['lat'])
    lng = float(info['lng'])
    zoom = float(info['zoom'])

    building_id = None
    if 'building_id' in info:
        building_id = info['building_id']

    global mrcnn
    if mrcnn is not None:
        building_id = mrcnn.delete_mask(lat, lng, zoom, building_id)

        json_post = {"rects_to_delete":
                         {"ids": [building_id]}
                     }
        return json_post

    return 'mrcnn has not been made'


def result_to_dict(result):
    info = {}
    for k, v in result.items():
        info[k.lower()] = v
    return info

def get_imd():
    # do imd = get_imd() in all functions
    config = config_reader.get_config()
    return imagery.ImageryDownloader(config['accessKey'])
