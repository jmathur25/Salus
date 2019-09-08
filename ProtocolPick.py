from flask import jsonify, request, render_template
import mysql.connector
from flask import Blueprint
import  json
from Person import get_file_contents, getAdminPhoneNums
import imagery
# from application import get_program_config
from twilio.rest import Client
import config_reader


protocol_pick  = Blueprint('protocol_pick', __name__)


@protocol_pick.route('/getProtocols')
def getProtocols():
    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')

    query = """
        Select * from Protocols Where schoolName = "UIUC"
    """
    cursor = cnx.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    retList = []
    for res in result:
        retList.append( {"id": res[0], "schoolName": res[1], "protocolName": res[2], "initialInstruction": res[3], "type": res[4] } )

    return retList


@protocol_pick.route('/')
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


    return render_template('Protocols.html', protocols=getProtocols(), **context)


@protocol_pick.route('/setup', methods=['POST'])
def setup():
    # from .setup import ...
    return "success"


@protocol_pick.route('/setup/corners', methods=['POST'])
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


@protocol_pick.route('/setup/delete', methods=['POST'])
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