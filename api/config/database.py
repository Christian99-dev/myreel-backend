from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
LOCAL_DB        = os.getenv("LOCAL_DB")

MYSQL_HOST      = os.getenv("MYSQL_HOST")       if not LOCAL_DB else os.getenv("MYSQL_HOST_LOCAL")
MYSQL_USER      = os.getenv("MYSQL_USER")       if not LOCAL_DB else os.getenv("MYSQL_USER_LOCAL")
MYSQL_PASSWORD  = os.getenv("MYSQL_PASSWORD")   if not LOCAL_DB else os.getenv("MYSQL_PASSWORD_LOCAL")
MYSQL_DB        = os.getenv("MYSQL_DB")         if not LOCAL_DB else os.getenv("MYSQL_DB_LOCAL")

URL_DATABASE = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
engine = create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()
 



