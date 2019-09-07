import os
import shutil
import numpy as np
import json
from Person import person
from MessageBoard import message_board
from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, send_file

# my own files
import config_reader
import imagery
import geolocation

# EB looks for an 'application' callable by default.
application = Flask(__name__)
application.register_blueprint(person, url_prefix="/person" )
application.register_blueprint(message_board, url_prefix="/message" )


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
    return imagery.ImageryDownloader(config["imageryURL"], config["accessKey"])

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

    # Create imagery downloader
    imd = imagery.ImageryDownloader(imagery_url, access_key)

    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True

    # runs the app
    application.run()

    
