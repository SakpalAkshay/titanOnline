
PRAGMA foreign_keys=ON;

CREATE TABLE Students(
student_id INT unsigned NOT NULL,
student_name VARCHAR(30) NOT NULL, 
max_waiting_lists INT unsigned, 
PRIMARY KEY (student_id)
);