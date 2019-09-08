-- Alter Table GeoFeatures add Column xTile INT; 
-- Alter Table GeoFeatures add Column yTile INT;
-- Alter Table GeoFeatures modify Column structureType VARCHAR(255); 


Select MAX(idBuilding) + 1 From GeoFeatures;

Insert Into GeoFeatures(idBuilding, latitude, longitude, xTile, yTile, schoolName, structureType) values (2, 1,3,4,5,"UIUC", "building"); 
Select * from GeoFeatures;