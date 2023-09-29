

PRAGMA foreign_keys=ON;

CREATE TABLE Drop(
    DropedStudent INT unsigned NOT NULL, 
    RelatedClass INT unsigned NOT NULL,
    FOREIGN KEY (DropedStudent) REFERENCES Students(student_id),
    FOREIGN KEY (RelatedClass) REFERENCES classes(class_id),
    PRIMARY KEY (EnrolledStudent, RelatedClass) 
);