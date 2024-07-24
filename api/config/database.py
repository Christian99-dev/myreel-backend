import os
import logging
from typing import Annotated
from dotenv import load_dotenv
from fastapi.params import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from api.models.database import model
from test.utils.fill_test_model import fill_test_model
from api.utils.database.print_database_contents import print_database_contents
from distutils.util import strtobool
logger = logging.getLogger("testing")

load_dotenv()
LOCAL_DB = strtobool(os.getenv("LOCAL_DB"))

if LOCAL_DB:
    SQLITE_DB_PATH  = os.getenv("SQLITE_DB_PATH")
    URL_DATABASE    = f"sqlite:///{SQLITE_DB_PATH}"
else:
    MYSQL_HOST      = os.getenv("MYSQL_HOST")
    MYSQL_USER      = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD  = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB        = os.getenv("MYSQL_DB")
    URL_DATABASE    = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"

# Start con
engine  = create_engine(URL_DATABASE, connect_args={"check_same_thread": False} if LOCAL_DB else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#pverride model if needed
model.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

with SessionLocal() as session:
     # Wenn die Tabelle leer ist, die Datenbank füllen
    if not session.query(model.User).first() and LOCAL_DB:
        fill_test_model(session)
    
    print_database_contents(session, {
        'Slot':         False,
        'Song':         False,
        'Edit':         False,
        'Group':        False,
        'Invitation':   False,
        'User':         False,
        'LoginRequest': False,
        'OccupiedSlot': False
    })