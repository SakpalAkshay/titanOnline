-- worried it need a USE command since my old sql code has it to access the db I believe

PRAGMA foreign_keys=ON;
CREATE TABLE Instructors(
instructor_id INT unsigned NOT NULL,
-- might be able to assign this randomly with out making it (the id)
instructor_name VARCHAR(30) NOT NULL,
offeredClass INT unsigned NOT NULL, 
-- named the class id differently to make sense in calling it from this table
PRIMARY KEY (instructor_id),
FOREIGN KEY (offeredClass) REFERENCES classes(class_id)
);
