import contextlib
import collections
import sqlite3
from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseModel
from pydantic_settings import BaseSettings
import logging.config


class Settings(BaseSettings, env_file=".env", extra="ignore"):
    database: str
    logging_config: str


class EnrollmentData(BaseModel):
    student_id: int
    class_id: int


class Class(BaseModel):
    class_id: int
    department_id: int
    department_name: str
    course_code: str
    section_number: str
    class_name: str
    instructor_id: int
    current_enrollment: int
    max_enrollment: int
    is_enrollment_frozen: bool
    waiting_list_size: int


class DeleteSection(BaseModel):
    class_id: int
    section_number: str


class UpdateInstructor(BaseModel):
    class_id: int
    instructor_id: int


def get_db():
    with contextlib.closing(sqlite3.connect(settings.database)) as db:
        db.row_factory = sqlite3.Row
        yield db


def get_logger():
    return logging.getLogger(__name__)


settings = Settings()
app = FastAPI()
logging.config.fileConfig(settings.logging_config, disable_existing_loggers=False)


# List available classes
@app.get("/listAllClasses/", status_code=200, )
def listAllClasees(db: sqlite3.Connection = Depends(get_db), logger: logging.Logger = Depends(get_logger)):
    logger.info("Started service GET: List All Classes")
    try:
        classes = db.execute("SELECT * FROM classes")
        logger.info("Class Data Returned successfully")
        return classes.fetchall()
    except sqlite3.IntegrityError:
        logger.error("Sqlite3 Integrity Eror, Problem in Connection")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Attempt to enroll in a class
@app.put("/student/enrollClass/", status_code=201)
def enrollInClass(dataForEnrollment: EnrollmentData, db: sqlite3.Connection = Depends(get_db),
                  logger: logging.Logger = Depends(get_logger)):
    logger.info("Started PUT request - Student/EnrollInClass")
    logger.info("Recieved Parameters: " + "Student ID: " + str(dataForEnrollment.student_id) + " Class ID: " + str(
        dataForEnrollment.class_id))
    try:
        classInfo = db.execute("SELECT * FROM classes WHERE class_id=?", (dataForEnrollment.class_id,))
        classData = classInfo.fetchone()
        logger.info("Fetched Class Data:", classData)
        studentInfo = db.execute("SELECT * FROM students WHERE student_id=?", (dataForEnrollment.student_id,))
        studentData = studentInfo.fetchone()
        logger.info("Fetched Student Data:", studentData)
        if not classData or not studentData:
            logger.error("Class or Student Id not found")
            raise HTTPException(status_code=404, detail="Details provided doesn't exist")

        if classData['is_enrollment_frozen']:
            logger.error("Operation Aborted: Enrollment already frozen")
            raise HTTPException(status_code=405, detail="Enrollment Frozen")

        # update this if to accomodate pushing into waiting list
        if classData['current_enrollment'] >= classData['max_enrollment']:
            # check if student crossed max waitlist enrollment if they did then raise error
            logger.info("Class full, pushing student to wailist")
            if (studentData['max_waiting_lists'] >= 3):
                logger.warn("Operation Aborted: Max Wailist Size full for student")
                raise HTTPException(status_code=400,
                                    detail="Enrollment frozen for current class, max waitlist enrollment reached")

            waitlistInfo = db.execute('SELECT COUNT(*) FROM waitlists WHERE class_id=?', (dataForEnrollment.class_id,))
            wlSize = waitlistInfo.fetchone()
            if wlSize:  # the waitlist doesnt exist and we need to create one
                wailtListSize = wlSize['COUNT(*)']
            else:
                wailtListSize = 0

            newPosition = wailtListSize + 1
            try:
                db.execute('''INSERT INTO waitlists (student_id, class_id, position, date_added) VALUES (?,?,?, DATE('now'))
                ''', (dataForEnrollment.student_id, dataForEnrollment.class_id, newPosition))
                db.commit()
                logger.info("Student Added to waitlist")

                return {'Info': "Class already full, Entry added to Waiting list Successfully"}

            except sqlite3.IntegrityError:
                logger.error("Student is already in waiting list")
                raise HTTPException(status_code=400, detail="Enrollment already exist in waiting list")

        try:
            db.execute("INSERT INTO enrollments (student_id, class_id) VALUES (?, ?)",
                       (dataForEnrollment.student_id, dataForEnrollment.class_id))
            logger.info("Entry added to Enrollments")
        except sqlite3.IntegrityError:
            logger.error("Student is already enrolled")
            raise HTTPException(status_code=400, detail="Enrollment already exist")

        db.execute("UPDATE classes SET current_enrollment = current_enrollment + 1 WHERE class_id =?",
                   (dataForEnrollment.class_id,))
        db.commit()
        logger.info("Student Enrollment is succesfull")
        return {"Info": "Class Enrolled Successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/student/waitlist/{class_id}")
# View position on waiting list
def waitlistPosition(class_id: int, student_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        waitinglistInfo = db.execute('SELECT position FROM waitlists WHERE class_id = ? and student_id = ?',
                                     (class_id, student_id))
        positionData = waitinglistInfo.fetchone()
        # If student is in waitlist return position if not student is not on wait list
        if positionData:
            return {"position": positionData['position']}
        else:
            return {"position": None}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.delete("/student/removeFromWaitlist/{class_id}")
# Implementing ability for students to leave waitlist
def removeFromWaitlist(class_id: int, student_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        db.execute('DELETE FROM waitlists WHERE class_id = ? AND student_id = ?', (class_id, student_id))
        db.commit()
        return {"Info": "Removed from the waiting list successfully"}

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/instructor/waitlist/{class_id}")
# Implementing ability for Instructors to view waitlist
def viewWaitlist(class_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        waitlistInfo = db.execute(
            'SELECT students.student_id, students.student_name, waitlists.position '
            'FROM waitlists '
            'INNER JOIN students ON waitlists.student_id = students.student_id '
            'WHERE waitlists.class_id = ? '
            'ORDER BY waitlists.date_added ASC',
            (class_id,)
        )
        waitingList = waitlistInfo.fetchall()
        return {"waitlist": waitingList}

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.put("/student/dropClass/", status_code=200)
def dropClass(dataForEnrollment: EnrollmentData, db: sqlite3.Connection = Depends(get_db),
              logger: logging.Logger = Depends(get_logger)):
    logger.info("Started Service - Student/DropClass")
    # Implement updating the enrollment table i.e drop student from Enrollment table with some student id and classId
    try:
        enrollmentInfo = db.execute('SELECT * FROM enrollments WHERE student_id = ? AND class_id = ?',
                                    (dataForEnrollment.student_id, dataForEnrollment.class_id))
        enrollmentData = enrollmentInfo.fetchone()
        if not enrollmentData:
            logger.error("Enrollment Doesn't exist for student id : " + str(
                dataForEnrollment.student_id) + " for class id: " + str(dataForEnrollment.class_id))
            raise HTTPException(status_code=404, detail="Enrollment doesn't exist")

        try:
            db.execute('INSERT INTO drops(student_id, class_id) VALUES (?,?)',
                       (dataForEnrollment.student_id, dataForEnrollment.class_id))
            logger.info('Student Added to dropped table, StudentId: ' + str(dataForEnrollment.student_id))
        except sqlite3.IntegrityError:
            logger.error("Class has already been dropped")
            raise HTTPException(status_code=400, detail="This class is already droppped")

        db.execute('DELETE FROM enrollments WHERE student_id = ? AND class_id = ?',
                   (dataForEnrollment.student_id, dataForEnrollment.class_id))
        logger.info("Studnet Dropped from enrollments successfully")
        # push one entry from wailtlist to Enrollment if enrollment for that class is not frozen
        classInfo = db.execute('SELECT * FROM classes WHERE class_id = ?', (dataForEnrollment.class_id,))
        classData = classInfo.fetchone()

        if not classData['is_enrollment_frozen']:
            logger.info("Pushing entry from waitlist to enrollments")
            # fetch student data whose position is 1 in that class
            studentInfo = db.execute('SELECT * FROM waitlists WHERE class_id =? AND position = ?',
                                     (dataForEnrollment.class_id, 1))
            studentData = studentInfo.fetchone()
            if studentData:
                db.execute('INSERT INTO enrollments (student_id, class_id) VALUES (?,?)',
                           (studentData['student_id'], studentData['class_id']))
                db.execute('DELETE FROM waitlists WHERE class_id =? AND position = ?', (dataForEnrollment.class_id, 1))

                # Update positions of waitlist students
                db.execute('UPDATE waitlists SET position = position - 1 WHERE class_id = ? AND position > 1',
                           (dataForEnrollment.class_id,))
                db.commit()
                logger.info("Student push from waitlist to enrollment: Successful")
                return {"Info": "Class Dropped Successfully, student from waitlist got enrolled in Class"}
        db.execute('UPDATE classes SET current_enrollment = current_enrollment - 1 WHERE class_id = ?',
                   (dataForEnrollment.class_id,))
        db.commit()
        logger.info("Class classID: " + str(dataForEnrollment.class_id) + "is dropped for studentID: " + str(
            dataForEnrollment.student_id))
        return {"Info": "Class dropped successfully"}
    except sqlite3.IntegrityError:
        logger.error("Problem in database connection or SQL query")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/addClasseSection", status_code=201)
def add_class(classes: Class, db: sqlite3.Connection = Depends(get_db)):
    try:

        # Check to see if class already exists first.
        q_exists = db.execute(
            "SELECT * FROM classes WHERE class_id = ?", (classes.class_id,))
        if q_exists.fetchone():
            raise HTTPException(
                status_code=500, detail="Class Already Exists!")

        # Add class section into database.
        db.execute("INSERT INTO classes VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                   (classes.class_id,
                    classes.department_id,
                    classes.department_name,
                    classes.course_code,
                    classes.section_number,
                    classes.class_name,
                    classes.instructor_id,
                    classes.current_enrollment,
                    classes.max_enrollment,
                    classes.is_enrollment_frozen,
                    classes.waiting_list_size))
        db.commit()

        return {"{} Section {} has been added.".format(classes.course_code, classes.section_number)}

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.delete("/deleteSection/", status_code=200)
def delete_section(delete: DeleteSection, db: sqlite3.Connection = Depends(get_db)):
    try:
        # If class exists, delete from database. Else deny request.
        q_exists = db.execute(
            "SELECT * FROM classes WHERE class_id = ?", (delete.class_id,))
        q_exists = q_exists.fetchone()
        if q_exists:
            # Delete from Classes
            db.execute("DELETE FROM classes WHERE class_id = ? AND section_number = ?",
                       (delete.class_id, delete.section_number))
            db.commit()

            # Delete from Enrollment
            db.execute(
                "DELETE FROM enrollments WHERE class_id = ?", (delete.class_id,))
            db.commit()

            # Delete from Waitlist
            db.execute("DELETE FROM waitlists WHERE class_id = ?",
                       (delete.class_id,))
            db.commit()

            # Delete from Drop
            db.execute("DELETE FROM drops WHERE class_id = ?",
                       (delete.class_id,))
            db.commit()

            return {
                "Class id {} Section {} successfully deleted.".format(q_exists['course_code'], delete.section_number)}

        raise HTTPException(status_code=500, detail="Class does not Exist")

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.put("/updateInstructor", status_code=201)
def update_instructor(update: UpdateInstructor, db: sqlite3.Connection = Depends(get_db)):
    try:
        # Check for existance of class with that chosen instructor.
        q_exists = db.execute(
            "SELECT * FROM classes WHERE class_id = ?", (update.class_id,))
        q_exists = q_exists.fetchone()

        q_exists_2 = db.execute(
            "SELECT * FROM instructors WHERE instructor_id = ?", (
                update.instructor_id,)
        )
        q_exists_2 = q_exists_2.fetchone()

        if q_exists and q_exists_2:
            db.execute("UPDATE classes SET instructor_id = ? WHERE class_id = ?",
                       (update.instructor_id, update.class_id))
            db.commit()
            return {"Class instructor for {} has been updated to {}".format(q_exists["course_code"],
                                                                            q_exists_2["instructor_name"])}

        raise HTTPException(
            status_code=500, detail="There was a problem with the class or instructor information.")
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.put("/freezeWaitlist/{freeze}", status_code=201)
def update(freeze: bool, db: sqlite3.Connection = Depends(get_db)):
    try:
        db.execute("UPDATE classes SET is_enrollment_frozen = ?", (freeze,))
        db.commit()

        if freeze:
            return {"Waitlist Enrollment is now frozen."}
        return {"Waitlist Enrollment is open"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/instructor/viewEnrollment/{instructor_id}")
def viewEnrollment(instructor_id: str, db: sqlite3.Connection = Depends(get_db)):
    try:
        instructorInfo = db.execute('SELECT class_id,current_enrollment FROM classes WHERE instructor_id =?',
                                    (instructor_id))
        instructorData = instructorInfo.fetchall()
        if not instructorData:
            raise HTTPException(status_code=404, detail="Details provided doesn't exist")

        return instructorData

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/instructor/dropStudent/")
def dropStudent(dataForEnrollment: EnrollmentData, db: sqlite3.Connection = Depends(get_db)):
    # Implement updating the enrollment table i.e drop student from Enrollment table with some student id and classId
    try:
        enrollmentInfo = db.execute('SELECT * FROM enrollments WHERE student_id = ? AND class_id = ?',
                                    (dataForEnrollment.student_id, dataForEnrollment.class_id))
        enrollmentData = enrollmentInfo.fetchone()
        if not enrollmentData:
            raise HTTPException(status_code=400, detail="Enrollment doesn't exist")
        db.execute('DELETE FROM enrollments WHERE student_id = ? AND class_id = ?',
                   (dataForEnrollment.student_id, dataForEnrollment.class_id))
        # push one entry from wailtlist to Enrollment if enrollment for that class is not frozen
        classInfo = db.execute('SELECT * FROM classes WHERE class_id = ?', (dataForEnrollment.class_id))
        classData = classInfo.fetchone()
        if not classData['is_enrollment_frozen']:
            # fetch student data whose position is 1 in that class
            studentInfo = db.execute('SELECT * FROM waitlists WHERE class_id =? AND position = ?',
                                     (dataForEnrollment.class_id, 1))
            studentData = studentInfo.fetchone()
            if studentData:
                db.execute('INSERT INTO enrollments (student_id, class_id) VALUES (?,?)',
                           (studentData['student_id'], studentData['class_id']))
                db.execute('DELETE FROM waitlists WHERE class_id =? AND position = ?',
                           (dataForEnrollment.class_id, 1))
                # Update positions of waitlist students
                db.execute('UPDATE waitlists SET position = position - 1 WHERE class_id = ? AND position > 1',
                           (dataForEnrollment.class_id,))
                db.commit()
                return {"Info": "Class Dropped Successfully, student from waitlist got enrolled in Class"}
        db.execute('UPDATE classes SET current_enrollment = current_enrollment - 1 WHERE class_id = ?',
                   (dataForEnrollment.class_id,))
        db.commit()
        return {"Info": "Class dropped successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@app.get("/instructor/viewDroppedStudents/{class_id}")
def viewDroppedStudents(class_id: str, db: sqlite3.Connection = Depends(get_db)):
    try:
        dropListInfo = db.execute('SELECT students.student_id, students.student_name, drops.class_id '
                                  'FROM drops INNER JOIN students ON drops.student_id = students.student_id '
                                  'WHERE drops.class_id = ?', (class_id))
        dropListData = dropListInfo.fetchall()
        if not dropListData:
            raise HTTPException(status_code=404, detail="Details provided doesn't exist")
        return dropListData
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=500, detail="Internal Server Error")