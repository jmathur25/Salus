Create Table MessageBoard(
	personId Int, 
    message VARCHAR(255), 
	updated_at TIMESTAMP NOT NULL DEFAULT NOW() ON UPDATE NOW(),
	created_at TIMESTAMP NOT NULL DEFAULT NOW()
)