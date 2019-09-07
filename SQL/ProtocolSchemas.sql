Create Table Protocols(
	id INT not Null primary key AUTO_INCREMENT,
    schoolName VARCHAR(255), 
    protocolName VARCHAR(255), 
    initialInstruction VARCHAR(255)
);

Create Table ProtocolToBuilding(
	id INT not Null primary key AUTO_INCREMENT,
    protocolID INT, 
	buildingID INT

);

Create Table ProtocolStatusInitial(
	id INT not Null primary key AUTO_INCREMENT,
	buildingID INT, 
    protocolName VARCHAR(255),
    buildingStatus VARCHAR(255)
); 

Create Table ProtocolStatusCurrent(
	id INT not Null primary key AUTO_INCREMENT,
	buildingID INT, 
    buildingStatus VARCHAR(255),
    schoolName VARCHAR(255),
	updated_at TIMESTAMP NOT NULL DEFAULT NOW() ON UPDATE NOW(),
	created_at TIMESTAMP NOT NULL DEFAULT NOW()
); 