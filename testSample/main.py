import collections
import contextlib
import logging.config
import sqlite3
import typing

from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Settings(BaseSettings, env_file=".env", extra="ignore"):
    database: str
    #logging_config: str


class EnrollmentData(BaseModel):
    student_id: int
    class_id: int
   


def get_db():
    with contextlib.closing(sqlite3.connect(settings.database)) as db:
        db.row_factory = sqlite3.Row
        yield db


#def get_logger():
    #return logging.getLogger(__name__)


settings = Settings()
app = FastAPI()

#logging.config.fileConfig(settings.logging_config, disable_existing_loggers=False)

@app.get("/listAllClasses/")
def listAllClasees(db: sqlite3.Connection = Depends(get_db)):
    try:
        classes = db.execute("SELECT * FROM classes")
        return  classes.fetchall()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=500, detail="Internal Server Error")


#code to fetch enrolled student based upon student id
#@app.get("/enrollmentsData/{classId}")
#def enrollments(classId:int, db: sqlite3.Connection = Depends(get_db)):
    #enrolls = db.execute('''SELECT enrollments.*, classes.*, students.*
#FROM enrollments
#INNER JOIN classes ON enrollments.class_id = classes.class_id
#INNER JOIN students ON enrollments.student_id = students.student_id
#WHERE enrollments.class_id = ?
#''',(classId,))
#    return  enrolls.fetchall()

@app.put("/student/enrollClass/")
def enrollInClass(dataForEnrollment:EnrollmentData, db: sqlite3.Connection = Depends(get_db)):
    try:
        classInfo = db.execute("SELECT * FROM classes WHERE class_id=?",(dataForEnrollment.class_id,))
        classData = classInfo.fetchone()
        
        studentInfo = db.execute("SELECT * FROM students WHERE student_id=?", (dataForEnrollment.student_id,))
        studentData = studentInfo.fetchone()
        if not classData or not studentData:
            raise HTTPException(status_code=404, detail="Details provided doesn't exist")
        
        if classData['is_enrollment_frozen']:
            raise HTTPException(status_code=400, detail="Enrollment Frozen")
        #return classData
    #update this if to accomodate pushing into waiting list
        if classData['current_enrollment'] >= classData['max_enrollment']:
            #check if student crossed max waitlist enrollment if they did then raise error
            if (studentData['max_waiting_lists'] >= 3):
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
                return {'Info': "Class already full, Entry added to Waiting list Successfully"}

            except sqlite3.IntegrityError:
                raise HTTPException(status_code=400, detail="Enrollment already exist in waiting list")

        
        try:   
            db.execute("INSERT INTO enrollments (student_id, class_id) VALUES (?, ?)", (dataForEnrollment.student_id,dataForEnrollment.class_id))
        
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Enrollment already exist")
        
        db.execute("UPDATE classes SET current_enrollment = current_enrollment + 1 WHERE class_id =?",(dataForEnrollment.class_id,))
        db.commit()
        return {"Info": "Class Enrolled Successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=500, detail="Internal Server Error")
      

@app.put("/student/dropClass/")
def dropClass(dataForEnrollment:EnrollmentData, db: sqlite3.Connection = Depends(get_db) ):
    #Implement updating the enrollment table i.e drop student from Enrollment table with some student id and classId
    try:
        enrollmentInfo = db.execute('SELECT * FROM enrollments WHERE student_id = ? AND class_id = ?', (dataForEnrollment.student_id, dataForEnrollment.class_id))
        enrollmentData = enrollmentInfo.fetchone()
        if not enrollmentData:
            raise HTTPException(status_code=400, detail="Enrollment doesn't exist")
        db.execute('DELETE FROM enrollments WHERE student_id = ? AND class_id = ?', (dataForEnrollment.student_id, dataForEnrollment.class_id))
    
        # push one entry from wailtlist to Enrollment if enrollment for that class is not frozen
        classInfo = db.execute('SELECT * FROM classes WHERE class_id = ?', (dataForEnrollment.class_id))
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
        




