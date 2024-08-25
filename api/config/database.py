import os
import logging
from typing import Annotated
from dotenv import load_dotenv
from fastapi.params import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from distutils.util import strtobool
from api.models.database.model import Base

logger = logging.getLogger("testing")

load_dotenv()
LOCAL_DB = strtobool(os.getenv("LOCAL_DB"))

if LOCAL_DB:
    URL_DATABASE    = f"sqlite:///./local.db"
else:
    MYSQL_HOST      = os.getenv("MYSQL_HOST")
    MYSQL_USER      = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD  = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB        = os.getenv("MYSQL_DB")
    
    URL_DATABASE    = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"

engine = create_engine(URL_DATABASE, connect_args={"check_same_thread": False} if LOCAL_DB else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# get session for local / server
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


# ram database for unittest        
def get_db_memory():
    """Creates and configures the database engine and session."""
    # Erstelle die Engine
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

    # Erstelle die Tabellen im Vorfeld
    Base.metadata.create_all(bind=engine)

    # Session-Maker für zukünftige Sessions
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Setup einer leeren Session
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session  # Gibt die Session zurück
    finally:
        # Teardown: Schließe die Session und rolle die Transaktion zurück
        session.close()
        transaction.rollback()
        connection.close()

        # Entferne die Tabellen nach den Tests
        Base.metadata.drop_all(bind=engine)
        



