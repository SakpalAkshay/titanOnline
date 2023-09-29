PRAGMA foreign_keys=ON;

CREATE TABLE Enrollments(
    enrolledStudent INT unsigned NOT NULL, 
    relatedClass INT unsigned NOT NULL,
    FOREIGN KEY (EnrolledStudent) REFERENCES Students(student_id),
    FOREIGN KEY (RelatedClass) REFERENCES classes(class_id),
    PRIMARY KEY (EnrolledStudent, RelatedClass) 
);