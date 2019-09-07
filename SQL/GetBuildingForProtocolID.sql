Select protocolID, ProtocolSynthesis.buildingID, latitude, longitude, schoolName, ProtocolSynthesis.buildingStatus, updated_at, created_at
From (
		Select ProtocolToBuilding.protocolID, ProtocolStatusInitial.buildingID 
        From ProtocolToBuilding, ProtocolStatusInitial
        Where ProtocolToBuilding.protocolID = 1 and ProtocolStatusInitial.buildingID = ProtocolToBuilding.buildingID
        ) as ProtocolSynthesis Join GeoFeatures 
on buildingID = GeoFeatures.idBuilding AND schoolName = "UIUC"
order by created_at; 
