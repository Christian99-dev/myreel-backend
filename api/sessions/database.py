from abc import ABC, abstractmethod
import os
import logging
from typing import Any, Generator
from contextlib import contextmanager 
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from distutils.util import strtobool
from api.models.database.model import Base, Group, Song, User, Edit, Slot, Invitation, LoginRequest, OccupiedSlot
from api.utils.database.print_database_contents import print_database_contents
from mock.database.data import data


"""ENV"""
load_dotenv()
DATABASE_LOCAL                       = bool(strtobool(os.getenv("DATABASE_LOCAL")))
DATABASE_LOCAL_FILL                  = bool(strtobool(os.getenv("DATABASE_LOCAL_FILL")))

DATABASE_REMOTE_SQL_HOST             = os.getenv("DATABASE_REMOTE_MYSQL_HOST")
DATABASE_REMOTE_SQL_USER             = os.getenv("DATABASE_REMOTE_MYSQL_USER")
DATABASE_REMOTE_SQL_PASSWORD         = os.getenv("DATABASE_REMOTE_MYSQL_PASSWORD")
DATABASE_REMOTE_SQL_DB               = os.getenv("DATABASE_REMOTE_MYSQL_DB")

"""Base Database Session Manager"""
class BaseDatabaseSessionManager(ABC):
    SessionLocal: sessionmaker = None

    @abstractmethod
    def __init__(self):
        """Initialisiert die Verbindung zur Datenbank."""
        pass

    @abstractmethod
    def get_session(self) -> Generator[Session, Any, None]:
        """Erzeugt eine Datenbank-Sitzung."""
        pass

    def _fill(self, data):
        """Füllt die Datenbank mit den Daten."""
        session = self.SessionLocal()
        try:
            self._clear()
            
            # Danach neue Daten einfügen
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
        """Druckt den Inhalt der Datenbank."""
        session = self.SessionLocal()
        try:
            print_database_contents(session, {
                'Group': True,
                'User': True,
                'LoginRequest': True,
                'Song': False,
                'Slot': False,
                'Edit': False,
                'Invitation': False,
                'OccupiedSlot': False
            })
        finally:
            session.close()

    def _clear(self):
        """Löscht den Inhalt der Datenbank."""
        session = self.SessionLocal()
        try:
            session.query(Group).delete()
            session.query(Song).delete()
            session.query(User).delete()
            session.query(Edit).delete()
            session.query(Slot).delete()
            session.query(Invitation).delete()
            session.query(LoginRequest).delete()
            session.query(OccupiedSlot).delete()
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


"""Implementations for Different Session Managers"""
class RemoteDatabaseSessionManager(BaseDatabaseSessionManager):
    def __init__(self):
        database_url = f"mysql+pymysql://{DATABASE_REMOTE_SQL_USER}:{DATABASE_REMOTE_SQL_PASSWORD}@{DATABASE_REMOTE_SQL_HOST}/{DATABASE_REMOTE_SQL_DB}"
        
        engine = create_engine(database_url)
        Base.metadata.create_all(bind=engine)
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_session(self) -> Generator[Session, Any, None]:
        database_session = self.SessionLocal()
        try:
            yield database_session
        finally:
            database_session.close()

class LocalDatabaseSessionManager(BaseDatabaseSessionManager):
    def __init__(self):
        os.makedirs("./outgoing/database", exist_ok=True)
        database_url = f"sqlite:///./outgoing/database/local.db"
        
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        if DATABASE_LOCAL_FILL:
            self._fill(data)
        self._print()

    def get_session(self) -> Generator[Session, Any, None]:
        database_session = self.SessionLocal()
        try:
            yield database_session
        finally:
            database_session.close()

class MemoryDatabaseSessionManager(BaseDatabaseSessionManager):
    def __init__(self):
        database_url = "sqlite:///:memory:"
        self.engine = create_engine(database_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=self.engine)

        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        self._fill(data)

    def get_session(self) -> Generator[Session, Any, None]:
        connection = self.engine.connect()
        transaction = connection.begin()
        session = self.SessionLocal(bind=connection)
        try:
            yield session
        finally:
            session.close()
            transaction.rollback()
            connection.close()

_database_session_manager = None

def get_database_session():
    global _database_session_manager
    
    # beim ersten ausführen
    if _database_session_manager is None:
        _database_session_manager = LocalDatabaseSessionManager() if DATABASE_LOCAL else RemoteDatabaseSessionManager()
    
    # Öffnet die Session und gibt sie zurück
    gen = _database_session_manager.get_session()
    session = next(gen)
    yield session