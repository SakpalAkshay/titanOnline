-- $ sqlite3 books.db < books.sql

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS classes;
CREATE TABLE classes (
    class_id INTEGER PRIMARY KEY,
    department_id INTEGER,
    department_name TEXT,
    course_code TEXT,
    section_number TEXT UNIQUE,
    class_name TEXT,
    instructor_id INTEGER,
    current_enrollment INTEGER,
    max_enrollment INTEGER,
    is_enrollment_frozen BOOLEAN,
    waiting_list_size INTEGER CHECK (waiting_list_size <= 15)
);

INSERT INTO classes (department_id, department_name, course_code, section_number, class_name, instructor_id, current_enrollment, max_enrollment, is_enrollment_frozen, waiting_list_size)
VALUES
    (1, 'Department 1', 'CS101', '001', 'Introduction to Computer Science', 1, 30, 50, 0, 5),
    (2, 'Department 2', 'MATH101', '002', 'Introduction to Mathematics', 2, 25, 40, 1, 10),
    (3, 'Department 3', 'PHYS101', '003', 'Introduction to Physics', 3, 35, 60, 0, 8);

COMMIT;

