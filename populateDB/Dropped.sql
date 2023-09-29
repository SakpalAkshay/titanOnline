

PRAGMA foreign_keys=ON;

CREATE TABLE Drop(
    dropedStudent INT unsigned NOT NULL, 
    relatedClass INT unsigned NOT NULL,
    FOREIGN KEY (dropedStudent) REFERENCES Students(student_id),
    FOREIGN KEY (relatedClass) REFERENCES classes(class_id),
    PRIMARY KEY (dropedStudent, relatedClass) 
);