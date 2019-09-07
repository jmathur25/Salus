from flask import jsonify, request, render_template
import mysql.connector
from flask import Blueprint
from Person import get_file_contents, getAdminPhoneNums
from twilio.rest import Client


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
def index():
    return render_template('Protocols.html', protocols=getProtocols())
