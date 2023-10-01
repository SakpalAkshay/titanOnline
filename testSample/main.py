import collections
import contextlib
import logging.config
import sqlite3
import typing

from fastapi import FastAPI, Depends, Response, HTTPException, status
#from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Settings(BaseSettings, env_file=".env", extra="ignore"):
    database: str
    #logging_config: str


#class Book(BaseModel):
    #published: int
    #author: str
    #title: str
    #first_sentence: str


def get_db():
    with contextlib.closing(sqlite3.connect(settings.database)) as db:
        db.row_factory = sqlite3.Row
        yield db


#def get_logger():
    #return logging.getLogger(__name__)


settings = Settings()
app = FastAPI()

#logging.config.fileConfig(settings.logging_config, disable_existing_loggers=False)

#class Enrollment(BaseModel):




@app.get("/listAllClasses/")
def listAllClasees(db: sqlite3.Connection = Depends(get_db)):
    classes = db.execute("SELECT * FROM classes")
    return {"classes": classes.fetchall()}



@app.get("/enrollInClass/{classId}/{sectionNo}")
def enrollInClass(classId:int, sectionNo:str, db: sqlite3.Connection = Depends(get_db)):
    classInfo = db.execute("SELECT * FROM classes WHERE section_number=? AND class_id=?",(sectionNo,classId))
    print(classInfo)
    return {"data":classInfo.fetchall()}
