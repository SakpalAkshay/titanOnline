PRAGMA foreign_keys=ON;

CREATE TABLE Enrollments(
    enrolledStudent INT unsigned NOT NULL, 
    relatedClass INT unsigned NOT NULL,
    FOREIGN KEY (enrolledStudent) REFERENCES Students(student_id),
    FOREIGN KEY (relatedClass) REFERENCES classes(class_id),
    PRIMARY KEY (enrolledStudent, relatedClass) 
);