import os
import shutil
import imagery
import geolocation
import numpy as np
import json
from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, send_file

app = Flask(__name__)

imd = None
program_config = {}

# useful function for turning request data into usable dictionaries
def result_to_dict(result):
    info = {}
    for k, v in result.items():
        info[k.lower()] = v
    return info

@app.route('/', methods=['GET'])  # base page that loads up on start/accessing the website
def login():  # this method is called when the page starts up
    return redirect('/home/')

@app.route('/home/')
def home():
    return render_template('DisplayMap.html')

@app.route('/home/mapclick', methods=['POST'])
def mapclick():
    if request.method == 'POST':
        result = request.form
        info = result_to_dict(result)
        print(info)

        # example of how to parse
        lat = float(info['lat'])
        long = float(info['long'])
        zoom = int(info['zoom'])
        
        # return json.dumps(json_post)

def start_webapp(config):
    """Starts the Flask server."""
    app.secret_key = 'super secret key'
    # app.config['SESSION_TYPE'] = 'filesystem'
    
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
    app.config['accessKey'] = program_config['accessKey']

    app.debug = True
    app.run()
