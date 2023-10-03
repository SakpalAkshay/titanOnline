PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS students;

CREATE TABLE students(
student_id INTEGER unsigned NOT NULL PRIMARY KEY,
student_name TEXT NOT NULL, 
max_waiting_lists INTEGER unsigned CHECK(max_waiting_lists between 0 and 3)
);

INSERT INTO students(student_id, student_name, max_waiting_lists)
VALUES
    (123, "Ken Alejandro", 0),
    (124, "Sophie Adams", 1),
    (125, "William Toast", 3),
    (126, "Jaiden Salior", 0),
    (122, "Marybeth Rose", 0),
    (121, "Gabriel Gonzales", 0),
    (127, "Romeo Daliez", 0),
    (128, "Gregory Miller", 2),
    (129, "Charlie Emily", 0),
    (130, "Mark Fischbach", 3);
COMMIT;
