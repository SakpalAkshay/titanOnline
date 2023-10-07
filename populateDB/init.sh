#!/bin/sh

sqlite3 ./titanOnline.db < ./classes.sql

sqlite3 ./titanOnline.db < ./students.sql

sqlite3 ./titanOnline.db < ./instructors.sql

sqlite3 ./titanOnline.db < ./Enrollments.sql

sqlite3 ./titanOnline.db < ./Dropped.sql

sqlite3 ./titanOnline.db < ./Waitlists.sql
