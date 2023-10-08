PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS enrollments;

CREATE TABLE enrollments(
    student_id  INT unsigned NOT NULL,  
    class_id INT unsigned NOT NULL,
    FOREIGN KEY (student_id ) REFERENCES Students(student_id),
    FOREIGN KEY (class_id) REFERENCES classes(class_id)
);
INSERT INTO enrollments(student_id, class_id)
VALUES
    (124, 3),
    (124, 2),
    (123, 1),
    (123, 2),
    (126, 2),
    (122, 1),
    (122, 2),
    (121, 1),
    (121, 2),
    (121, 3),
    (127, 2),
    (127, 3),
    (128, 3),
    (129, 1),
    (129, 2);
COMMIT;