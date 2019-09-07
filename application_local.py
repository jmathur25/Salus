import os
import shutil
import numpy as np
import json
from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, send_file

# my own files
import config_reader
import imagery
import geolocation

# EB looks for an 'application' callable by default.
application = Flask(__name__)

imd = None
program_config = {}

# useful function for turning request data into usable dictionaries
def result_to_dict(result):
    info = {}
    for k, v in result.items():
        info[k.lower()] = v
    return info

@application.route('/')
def home():
    return render_template('DisplayMap.html')

# @app.route('/home/mapclick', methods=['POST'])
# def mapclick():
#     if request.method == 'POST':
#         result = request.form
#         info = result_to_dict(result)
#         print(info)

#         # example of how to parse
#         lat = float(info['lat'])
#         long = float(info['long'])
#         zoom = int(info['zoom'])
        
        # return json.dumps(json_post)

# def start_webapp(config):
#     """Starts the Flask server."""
#     app.secret_key = 'super secret key'
#     # app.config['SESSION_TYPE'] = 'filesystem'
    
#     # Get config variables
#     if "imageryURL" not in config:
#         print("[ERROR] Could not find imageryURL in the config file!")

#     # Get the imagery URL and access key
#     imagery_url = config["imageryURL"]
#     access_key = ""

#     if "accessKey" in config:
#         access_key = config["accessKey"]

#     # Create imagery downloader
#     global imd
#     imd = imagery.ImageryDownloader(imagery_url, access_key)
    
#     global program_config
#     program_config = config

#     # add the program config access key to the app config
#     app.config['accessKey'] = program_config['accessKey']

#     app.debug = True
#     app.run()

# run the app.
if __name__ == "__main__":
        # """Starts the Flask server."""
    # app.secret_key = 'super secret key'

    config = config_reader.get_config()
    
    # Get config variables
    if "imageryURL" not in config:
        print("[ERROR] Could not find imageryURL in the config file!")

    # Get the imagery URL and access key
    imagery_url = config["imageryURL"]
    access_key = ""

    if "accessKey" in config:
        access_key = config["accessKey"]

    # Create imagery downloader
    global imd
    imd = imagery.ImageryDownloader(imagery_url, access_key)
    
    global program_config
    program_config = config

    # add the program config access key to the app config
    application.config['accessKey'] = program_config['accessKey']

    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True

    # runs the app
    application.run()

    
