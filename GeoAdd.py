from flask import jsonify, request
import mysql.connector
from flask import Blueprint
from Person import get_file_contents

zone = ["building", "field", "field", "building"]
point = [
            [(0,0), (6,0), (1,0), (0,6)],
            [(0,1), (0,0), (0,0), (5,0)],
            [(9,0), (0,1), (0,2), (0,3)],
            [(0,5), (3,0), (4,0), (2,0)],
         ]
tile = [(1,1), (69,420), (75,12), (85,65)]



def addAllGeo(zoneTypes, zonePoints, tileCoords):

    host_name = get_file_contents("HostDB");

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
        xCoord = tileCoords[i][0]
        yCoord = tileCoords[i][1]

        print(xCoord)
        print(yCoord)
        for zonePoint in zonePoints[i]:
            lat = zonePoint[0]
            lon = zonePoint[1]
            print(lat)
            print(lon)

            queryInsert = 'Insert Into GeoFeatures(idBuilding, latitude, longitude, xTile, yTile, schoolName, structureType) values (%s, %s,%s,%s,%s,"UIUC", %s); '
            cursor = cnx.cursor()
            print()
            cursor.execute(queryInsert, (buildingID, lat, lon, xCoord, yCoord, currentZoneName) )
            cnx.commit()


    return idSet;



print(addAllGeo(zone, point, tile))