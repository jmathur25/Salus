from flask import jsonify, request
import mysql.connector
from flask import Blueprint
from Person import get_file_contents



def addAllGeo(zoneTypes, zonePoints, tileCoords):

    host_name = get_file_contents("HostDB")

    cnx = mysql.connector.connect(user='root', password='Shatpass',
                                  host=host_name,
                                  database='innodb')

    assert len(zoneTypes) == len(zonePoints) == len(tileCoords)


    idSet = []
    for i in range(len(zoneTypes)):

        idQuery = """ 
                    Select MAX(idBuilding) + 1 
                    From 
                    GeoFeatures;
                 """

        cursor = cnx.cursor()
        cursor.execute(idQuery)
        result = cursor.fetchall()

        buildingID = result[0][0]
        print(buildingID)
        idSet.append(buildingID)


        currentZoneName = zoneTypes[i]
        print(currentZoneName)



        for j in range(len(zonePoints[i])):
            lat = zonePoints[i][j][0]
            lon = zonePoints[i][j][1]
            xCoord = tileCoords[i][j][0]
            yCoord = tileCoords[i][j][1]
            print(xCoord)
            print(yCoord)
            print(lat)
            print(lon)

            queryInsert = 'Insert Into GeoFeatures(idBuilding, latitude, longitude, xTile, yTile, schoolName, structureType) values (%s, %s,%s,%s,%s,"UIUC", %s); '
            cursor = cnx.cursor()
            print()
            cursor.execute(queryInsert, (buildingID, lat, lon, xCoord, yCoord, currentZoneName) )
            cnx.commit()


    return idSet

