
Create Table GeoFeatures (
	id INT not Null primary key AUTO_INCREMENT,
	idBuilding INT, 
    latitude DOUBLE, 
    longitude DOUBLE, 
    schoolName VARCHAR(255), 
	updated_at TIMESTAMP NOT NULL DEFAULT NOW() ON UPDATE NOW(),
	created_at TIMESTAMP NOT NULL DEFAULT NOW()
);