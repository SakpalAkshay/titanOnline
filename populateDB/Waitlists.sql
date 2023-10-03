PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS waitlists;

CREATE TABLE waitlists(
    student_id INT unsigned NOT NULL, 
    class_id INT unsigned NOT NULL,
    position Int unsigned NOT NULL,
    date_added TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (class_id) REFERENCES classes(class_id),
    PRIMARY KEY (student_id, class_id) 
);

INSERT INTO waitlists(student_id, class_id, date_added, position)

VALUES
    (125, 1, "2023-11-21", 1),
    (125, 2, "2023-11-22", 2),
    (125, 3, "2023-11-23", 3),
    (130, 1, "2023-11-24", 4),
    (130, 2, "2023-11-25", 5),
    (130, 3, "2023-12-15", 6),
    (128, 2, "2023-12-16", 7),
    (128, 1, "2023-12-18", 8),
    (124, 1, "2023-12-20", 9);
COMMIT;
