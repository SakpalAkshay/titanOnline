
PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS waitlists;

CREATE TABLE waitlists(
    student_id INT unsigned NOT NULL, 
    class_id INT unsigned NOT NULL,
    position Int unsigned NOT NULL,
    date_added DATE NOT NULL,
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (class_id) REFERENCES classes(class_id),
    PRIMARY KEY (student_id, class_id) 
);

INSERT INTO waitlists(student_id, class_id, date_added, position)

VALUES
    (125, 1, 2023-08-21, 3),
    (125, 2, 2023-01-18, 2),
    (125, 3, 2023-01-18, 1),
    (130, 1, 2024-01-18, 4),
    (130, 2, 2024-01-25, 5),
    (130, 3, 2024-02-15, 6),
    (128, 2, 2024-3-15, 7),
    (128, 1, 2024-3-15, 8),
    (124, 1, 2024-4-15, 9);
COMMIT;