Create Table EmergencyStatus(
	id INT not Null primary key AUTO_INCREMENT,
    school Varchar(255),
    emergencyType Varchar(255), 
    initialInstructions VARCHAR(255), 
	isActive boolean, 
	updated_at TIMESTAMP NOT NULL DEFAULT NOW() ON UPDATE NOW(),
	created_at TIMESTAMP NOT NULL DEFAULT NOW()

)