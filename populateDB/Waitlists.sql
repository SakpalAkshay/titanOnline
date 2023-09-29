
PRAGMA foreign_keys=ON;

CREATE TABLE Waitlists(
    waitingStudent INT unsigned NOT NULL, 
    waitingClass INT unsigned NOT NULL,
    position Int unsigned NOT NULL,
    date_added DATE NOT NULL,
    FOREIGN KEY (DropedStudent) REFERENCES Students(student_id),
    FOREIGN KEY (RelatedClass) REFERENCES classes(class_id),
    PRIMARY KEY (EnrolledStudent, RelatedClass) 
);