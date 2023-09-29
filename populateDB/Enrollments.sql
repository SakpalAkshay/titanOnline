PRAGMA foreign_keys=ON;

CREATE TABLE Enrollments(
    EnrolledStudent INT unsigned NOT NULL, 
    RelatedClass INT unsigned NOT NULL,
    FOREIGN KEY (EnrolledStudent) REFERENCES Students(student_id),
    FOREIGN KEY (RelatedClass) REFERENCES classes(class_id),
    PRIMARY KEY (EnrolledStudent, RelatedClass) 
);