import contextlib
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
   


def get_db():
    with contextlib.closing(sqlite3.connect(settings.database)) as db:
        db.row_factory = sqlite3.Row
        yield db

def get_logger():
    return logging.getLogger(__name__)

settings = Settings()
app = FastAPI()
logging.config.fileConfig(settings.logging_config, disable_existing_loggers=False)

#List available classes
@app.get("/listAllClasses/", status_code=200, )
def listAllClasees(db: sqlite3.Connection = Depends(get_db), logger: logging.Logger = Depends(get_logger)):
    logger.info("Started service GET: List All Classes")
    try:
        classes = db.execute("SELECT * FROM classes")
        logger.info("Class Data Returned successfully")
        return  classes.fetchall()
    except sqlite3.IntegrityError:
        logger.error("Sqlite3 Integrity Eror, Problem in Connection")
        raise HTTPException(status_code=500, detail="Internal Server Error")


#Attempt to enroll in a class
@app.put("/student/enrollClass/", status_code=201)
def enrollInClass(dataForEnrollment:EnrollmentData, db: sqlite3.Connection = Depends(get_db), logger: logging.Logger = Depends(get_logger)):
    logger.info("Started PUT request - Student/EnrollInClass")
    logger.info("Recieved Parameters: "+ "Student ID: "+ str(dataForEnrollment.student_id) + " Class ID: " + str(dataForEnrollment.class_id) )
    try:
        classInfo = db.execute("SELECT * FROM classes WHERE class_id=?",(dataForEnrollment.class_id,))
        classData = classInfo.fetchone()
        logger.info("Fetched Class Data:", classData )
        studentInfo = db.execute("SELECT * FROM students WHERE student_id=?", (dataForEnrollment.student_id,))
        studentData = studentInfo.fetchone()
        logger.info("Fetched Student Data:", studentData )
        if not classData or not studentData:
            logger.error("Class or Student Id not found")
            raise HTTPException(status_code=404, detail="Details provided doesn't exist")
        
        if classData['is_enrollment_frozen']:
            logger.error("Operation Aborted: Enrollment already frozen")
            raise HTTPException(status_code=405, detail="Enrollment Frozen")
       
    #update this if to accomodate pushing into waiting list
        if classData['current_enrollment'] >= classData['max_enrollment']:
            #check if student crossed max waitlist enrollment if they did then raise error
            logger.info("Class full, pushing student to wailist")
            if (studentData['max_waiting_lists'] >= 3):
                logger.warn("Operation Aborted: Max Wailist Size full for student")
                raise HTTPException(status_code=400, detail="Enrollment frozen for current class, max waitlist enrollment reached")

            waitlistInfo = db.execute('SELECT COUNT(*) FROM waitlists WHERE class_id=?', (dataForEnrollment.class_id,))
            wlSize = waitlistInfo.fetchone()
            if wlSize: #the waitlist doesnt exist and we need to create one
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
            db.execute("INSERT INTO enrollments (student_id, class_id) VALUES (?, ?)", (dataForEnrollment.student_id,dataForEnrollment.class_id))
            logger.info("Entry added to Enrollments")
        except sqlite3.IntegrityError:
            logger.error("Student is already enrolled")
            raise HTTPException(status_code=400, detail="Enrollment already exist")
        
        db.execute("UPDATE classes SET current_enrollment = current_enrollment + 1 WHERE class_id =?",(dataForEnrollment.class_id,))
        db.commit()
        logger.info("Student Enrollment is succesfull")
        return {"Info": "Class Enrolled Successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=500, detail="Internal Server Error")




#Drop a class
@app.put("/student/dropClass/", status_code=200)
def dropClass(dataForEnrollment:EnrollmentData, db: sqlite3.Connection = Depends(get_db) ):
    #Implement updating the enrollment table i.e drop student from Enrollment table with some student id and classId
    try:
        enrollmentInfo = db.execute('SELECT * FROM enrollments WHERE student_id = ? AND class_id = ?', (dataForEnrollment.student_id, dataForEnrollment.class_id))
        enrollmentData = enrollmentInfo.fetchone()
        if not enrollmentData:
            raise HTTPException(status_code=404, detail="Enrollment doesn't exist")
        
        try:
            db.execute('INSERT INTO drops(student_id, class_id) VALUES (?,?)', (dataForEnrollment.student_id, dataForEnrollment.class_id))
        
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="This class is already droppped")

        db.execute('DELETE FROM enrollments WHERE student_id = ? AND class_id = ?', (dataForEnrollment.student_id, dataForEnrollment.class_id))
    
        # push one entry from wailtlist to Enrollment if enrollment for that class is not frozen
        classInfo = db.execute('SELECT * FROM classes WHERE class_id = ?', (dataForEnrollment.class_id,))
        classData = classInfo.fetchone()


        if not classData['is_enrollment_frozen']:
            #fetch student data whose position is 1 in that class
            studentInfo = db.execute('SELECT * FROM waitlists WHERE class_id =? AND position = ?',(dataForEnrollment.class_id,1))
            studentData = studentInfo.fetchone()
            if studentData:
                db.execute('INSERT INTO enrollments (student_id, class_id) VALUES (?,?)', (studentData['student_id'], studentData['class_id']))
                db.execute('DELETE FROM waitlists WHERE class_id =? AND position = ?',(dataForEnrollment.class_id,1))

                #Update positions of waitlist students
                db.execute('UPDATE waitlists SET position = position - 1 WHERE class_id = ? AND position > 1', (dataForEnrollment.class_id,))
                db.commit()
                return {"Info" : "Class Dropped Successfully, student from waitlist got enrolled in Class"}
        db.execute('UPDATE classes SET current_enrollment = current_enrollment - 1 WHERE class_id = ?', (dataForEnrollment.class_id,))   
        db.commit()
        return {"Info": "Class dropped successfully"} 
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        

