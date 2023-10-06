import contextlib
import sqlite3
from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Settings(BaseSettings, env_file=".env", extra="ignore"):
    database: str


class EnrollmentData(BaseModel):
    student_id: int
    class_id: int
   


def get_db():
    with contextlib.closing(sqlite3.connect(settings.database)) as db:
        db.row_factory = sqlite3.Row
        yield db

settings = Settings()
app = FastAPI()


#List available classes
@app.get("/listAllClasses/", status_code=200)
def listAllClasees(db: sqlite3.Connection = Depends(get_db), status_code = 200):
    try:
        classes = db.execute("SELECT * FROM classes")
        return  classes.fetchall()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=500, detail="Internal Server Error")


#Attempt to enroll in a class
@app.put("/student/enrollClass/", status_code=201)
def enrollInClass(dataForEnrollment:EnrollmentData, db: sqlite3.Connection = Depends(get_db)):
    try:
        classInfo = db.execute("SELECT * FROM classes WHERE class_id=?",(dataForEnrollment.class_id,))
        classData = classInfo.fetchone()
        
        studentInfo = db.execute("SELECT * FROM students WHERE student_id=?", (dataForEnrollment.student_id,))
        studentData = studentInfo.fetchone()
        if not classData or not studentData:
            raise HTTPException(status_code=404, detail="Details provided doesn't exist")
        
        if classData['is_enrollment_frozen']:
            raise HTTPException(status_code=405, detail="Enrollment Frozen")
       
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

@app.put("dropClass/{classId}/{sectionNo}/{studentId}")
def dropClass(classId:int, sectionNo:str, studentId:int, db: sqlite3.Connection = Depends(get_db) ):
    #Implement updating the enrollment table i.e drop student from Enrollment table with some student id and classId
    pass
    #Imlement updating the dropped tables add student to the drop tables with class Id and section Id from which he has dropped
    #Update current enrollment count and automatically add someone from waiting list, freeze this enrollment after two weeks,and update the position count in 
    #waiting list

