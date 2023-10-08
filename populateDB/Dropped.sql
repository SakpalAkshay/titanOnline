
PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS drops;

CREATE TABLE drops(
    student_id INT unsigned NOT NULL, 
    class_id INT unsigned NOT NULL,
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (class_id) REFERENCES classes(class_id)
);

INSERT INTO drops(student_id, class_id)
    
VALUES 
    (123, 3),
    (129, 3);

COMMIT;