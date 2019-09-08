import os
import shutil
import numpy as np
import json
import csv
from Person import person
from MessageBoard import message_board
from EmergencyStatus import emergency_status
from GeoFeatures import geo_features
from ProtocolPick import protocol_pick
from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, send_file

# my own files
import config_reader
import imagery
import geolocation
from detectors.Detector import Detector

# server side scripts
import setup

# EB looks for an 'application' callable by default.
application = Flask(__name__)
application.register_blueprint(person, url_prefix="/person")
application.register_blueprint(message_board, url_prefix="/message")
application.register_blueprint(emergency_status, url_prefix="/emergency")
application.register_blueprint(geo_features, url_prefix="/building")
application.register_blueprint(protocol_pick, url_prefix="/protocolPicker")


mrcnn = None

# useful function for turning request data into usable dictionaries
def result_to_dict(result):
    info = {}
    for k, v in result.items():
        info[k.lower()] = v
    return info

# ideally, we can make this some shared-memory, maybe global variable assuming global vars don't fuck with REST
def get_program_config():
    # do config = get_program_config()
    return config_reader.get_config()

def get_imd():
    # do imd = get_imd() in all functions
    config = get_program_config()
    return imagery.ImageryDownloader(config['accessKey'])

@application.route('/', methods=['GET'])
def home(zoom=None, lat=None, lng=None):
    if lat is None or lng is None or zoom is None:
        config = get_program_config()
        lat = config['start_lat']
        lng = config['start_lng']
        zoom = config['start_zoom']

    access_key = get_program_config()['accessKey']
    context = {}
    context['lat'] = lat
    context['lng'] = lng
    context['zoom'] = zoom
    context['access_key'] = access_key
    return render_template('DisplayMap.html', **context)

@application.route('/<zoom>/<lat>/<lng>', methods=['GET'])
def move_to_new_lat_long(zoom, lat, lng):
    return home(zoom, lat, lng)

# ---- SETUP URLS ---- #

@application.route('/setup', methods=['POST'])
def setup_starter():
    # from .setup import ...
    return "success"

@application.route('/setup/create_zones', methods=['POST'])
def create_zones():
    result = request.form
    info = result_to_dict(result)
    print(info)
    keys = ['building_stack', 'field_stack']
    for k in keys:
        json_acceptable_string = info[k].replace("'", "\"")
        print(json_acceptable_string)
        parsed = json.loads(json_acceptable_string)
        info[k] = parsed
    setup.handle_zone_data(info)
    return 'success'

# --------- #

@application.route('/setup/corners', methods=['POST'])
def identify_region():
    result = request.form
    info = result_to_dict(result)
    lat = float(info['lat'])
    lng = float(info['lng'])
    zoom = float(info['zoom'])
    strategy = info['strategy']


    imd = get_imd()
    # old way, tabling for now...
    # image = imd.get_image_from_latlng_outline((lat1, lng1), (lat2, lng2))
    # image.save('setup/setup_image.png')
    # image = np.array(image) # detection needs an np array
    
    # find xtile, ytile
    xtile, ytile = geolocation.deg_to_tile(lat, lng, zoom)
    image = np.array(imd.download_tile(xtile, ytile, zoom))

    building_ids = None
    building_points = None

    if strategy == 'mrcnn':
        # SETUP MRCNN STUFF
        global mrcnn
        if mrcnn is None: # import if not already imported
            print('import MRCNN stuff...')
            from Mask_RCNN_Detect import Mask_RCNN_Detect
            mrcnn = Mask_RCNN_Detect('weights/epoch55.h5')

        mask_data = mrcnn.detect_building(image, lat, lng, zoom)
        building_ids = list(mask_data.keys())
        building_points = list(mask_data.values())

    else:
        detector = Detector(image, lat, lng, zoom)
        rect_id, rect_points = detector.detect_building()
        building_ids = [rect_id]
        building_points = [rect_points]

    print(building_points)

    json_post = {"rects_to_add": [{
                                "ids": building_ids,
                                "points": building_points
                            }],
            "rects_to_delete": {"ids": []}
                    }

    return json.dumps(json_post)

@application.route('/setup/delete', methods=['POST'])
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

# run the app.
if __name__ == "__main__":
    config = config_reader.get_config()

    REQUIRED_KEYS = ['imageryURL', 'accessKey', 'start_lat', 'start_lng', 'start_zoom']

    for k in REQUIRED_KEYS:
        if k not in config:
            print("[ERROR], REQUIRED KEY {} not in config".format(k))
        else:
            application.config[k] = config[k] # adds to the application config for access in templates

    # Get the imagery URL and access key
    imagery_url = config["imageryURL"]
    access_key = config["accessKey"]

    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True

    # runs the app
    application.run()

    
