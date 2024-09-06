from abc import ABC, abstractmethod
import os
import logging
from typing import Annotated, Any, Generator
from dotenv import load_dotenv
from fastapi.params import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from distutils.util import strtobool
from api.models.database.model import Base, Group,Song ,User ,Edit ,Slot ,Invitation ,LoginRequest ,OccupiedSlot
from api.utils.database.print_database_contents import print_database_contents
from mock.database.data import data
 
load_dotenv()
 
DATABASE_LOCAL = bool(strtobool(os.getenv("DATABASE_LOCAL")))

# TODO
# fill und print session local check und mit "with"

"""Base"""
class BaseDatabaseSessionManager(ABC):
    
    @abstractmethod
    def get_db_session(self) -> Session:
        pass
    
    def _fill(self, data):
        session = self.SessionLocal()
        try:
            # Alte Daten löschen
            session.query(Group).delete()
            session.query(Song).delete()
            session.query(User).delete()
            session.query(Edit).delete()
            session.query(Slot).delete()
            session.query(Invitation).delete()
            session.query(LoginRequest).delete()
            session.query(OccupiedSlot).delete()
            
            # Neue Daten einfügen
            session.bulk_insert_mappings(Group, data["groups"])
            session.bulk_insert_mappings(Song, data["songs"])
            session.bulk_insert_mappings(User, data["users"])
            session.bulk_insert_mappings(Edit, data["edits"])
            session.bulk_insert_mappings(Slot, data["slots"])
            session.bulk_insert_mappings(Invitation, data["invitations"])
            session.bulk_insert_mappings(LoginRequest, data["login_requests"])
            session.bulk_insert_mappings(OccupiedSlot, data["occupied_slots"])
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
    def _print(self):
        session = self.SessionLocal()
        try:
            print_database_contents(session, {
                'Slot':         False,
                'Song':         False,
                'Edit':         False,
                'Group':        True,
                'Invitation':   False,
                'User':         True,
                'LoginRequest': True,
                'OccupiedSlot': False
            })
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    
"""Implementations Local / Remote / Memory"""

class RemoteDatabaseSessionManager(BaseDatabaseSessionManager):
    def __init__(self):
        database_mysql_host      = os.getenv("DATABASE_MYSQL_HOST")
        database_mysql_user      = os.getenv("DATABASE_MYSQL_USER")
        database_mysql_password  = os.getenv("DATABASE_MYSQL_PASSWORD")
        database_mysql_db        = os.getenv("DATABASE_MYSQL_DB")
        database_url    = f"mysql+pymysql://{database_mysql_user}:{database_mysql_password}@{database_mysql_host}/{database_mysql_db}"
        
        engine = create_engine(database_url)
        Base.metadata.create_all(bind=engine)
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_db_session(self) -> Generator[Session, Any, None]:
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

class LocalDatabaseSessionManager(BaseDatabaseSessionManager):
    def __init__(self):
        database_local_fill = bool(strtobool(os.getenv("DATABASE_LOCAL_FILL")))
        
        database_local_repo = os.getenv("DATABASE_LOCAL_REPO")
        database_url    = f"sqlite:///./{database_local_repo}"
        
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        if database_local_fill:
            self._fill(data)
        self._print()
        
        
    def get_db_session(self)  -> Generator[Session, Any, None]:
        print("test")
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
class MemoryDatabaseSessionManager(BaseDatabaseSessionManager):
    def __init__(self):
        database_url = "sqlite:///:memory:"
        
        self.engine = create_engine(database_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=self.engine)
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        self._fill(data)
        
    def get_db_session(self) -> Generator[Session, Any, None]:
        connection = self.engine.connect()
        transaction = connection.begin()
        session = self.SessionLocal(bind=connection)
        
        try:
            yield session  
        finally:
            session.close()
            transaction.rollback()
            connection.close()


databaseSessionManager = LocalDatabaseSessionManager() if DATABASE_LOCAL else RemoteDatabaseSessionManager()