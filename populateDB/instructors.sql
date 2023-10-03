PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS instructors;

CREATE TABLE instructors(
instructor_id INT unsigned NOT NULL PRIMARY KEY,
-- might be able to assign this randomly with out making it (the id)
instructor_name VARCHAR(30) NOT NULL,
class_id INT unsigned NOT NULL, 
-- named the class id differently to make sense in calling it from this table
FOREIGN KEY (class_id) REFERENCES classes(class_id)
);

INSERT INTO instructors(instructor_id, instructor_name, class_id)
VALUES
    (1, "Aileen Johnson",2),
    (2, "Mark Carter",3),
    (3, "Sam Oak",1);
    
COMMIT;
