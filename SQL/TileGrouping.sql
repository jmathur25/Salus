Select *  
From ProtocolStatusCurrent; 


Select distinct buildingID, buildingStatus, GeoFeatures.schoolName, xTile, yTile, structureType 
from ProtocolStatusCurrent 
	Join GeoFeatures 
    on ProtocolStatusCurrent.buildingID = GeoFeatures.idBuilding 
    and ProtocolStatusCurrent.schoolName = GeoFeatures.schoolName;
    
    
    