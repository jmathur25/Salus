from flask import jsonify, request
import mysql.connector
from flask import Blueprint
from Person import get_file_contents, getAdminPhoneNums
from twilio.rest import Client

message_board  = Blueprint('message_board', __name__)


@message_board.route('/')
def index():
    return '/'



@message_board.route('/send', methods=['GET', 'POST'])
def sendMessage():

    host_name = get_file_contents("HostDB");

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')


    pid = request.args.get('pid')
    message = request.args.get('message')
    school = request.args.get('school')

    result = getAdminPhoneNums()
    sid = get_file_contents('sid.txt')
    authToken = get_file_contents('TwilioAuth.txt')
    client = Client(
        sid,
        authToken
    )
    for res in result:

        mes = client.messages.create(
            to= str(res[1]),
            from_ = '15087318632',
            body = "This is an automated message from: " + str(pid) + " \n " + str(message)

        )
        print(mes.sid)


    try:
        queryInsert = 'Insert Into MessageBoard(personId, message, schoolName) values (%s, %s, %s);'
        cursor = cnx.cursor()
        cursor.execute(queryInsert, (pid, str(message), school))
        cnx.commit()

        return jsonify(True)
    except Exception as e:
        print(e)
        return jsonify({"passed": False, "error": str(e)})
