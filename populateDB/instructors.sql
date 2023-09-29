-- worried it need a USE command since my old sql code has it to access the db I believe
CREATE TABLE instructors{
instructor_id INT unsigned NOT NULL,
-- might be able to assign this randomly with out making it (the id)
instructor_name VARCHAR(30) NOT NULL,
OfferedClass INT unsigned NOT NULL, 
-- named the class id differently to make sense in calling it from this table
PRIMARY KEY (instructor_id),
FOREIGN KEY (OfferedClass) REFERENCES classes(class_id)
}