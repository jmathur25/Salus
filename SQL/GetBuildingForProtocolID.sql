Select protocolID, ProtocolSynthesis.buildingID, latitude, longitude, schoolName, updated_at, created_at
From (
		Select *
        From ProtocolToBuilding
        Where ProtocolToBuilding.protocolID = 1
        ) as ProtocolSynthesis Join GeoFeatures 
on buildingID = GeoFeatures.idBuilding AND schoolName = "UIUC"
order by created_at; 
