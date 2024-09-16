import logging
from abc import ABC, abstractmethod
import os
from typing import Any, Generator
from contextlib import contextmanager
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from distutils.util import strtobool
from api.models.database.model import Base, Group, Song, User, Edit, Slot, Invitation, LoginRequest, OccupiedSlot
from api.utils.database.print_database_contents import print_database_contents
from mock.database.data import data
from sqlalchemy import select
from api.models.database import model
from tabulate import tabulate


#TODO DATABASE _PRINT SOLL DIE UTIL ERSETZEN, AUCH BEI FILES _PRINT 

# Logger für die Session-Verwaltung
logger = logging.getLogger("sessions.database")

"""ENV"""
load_dotenv()
DATABASE_LOCAL                      = bool(strtobool(os.getenv("DATABASE_LOCAL")))
DATABASE_LOCAL_FILL                 = bool(strtobool(os.getenv("DATABASE_LOCAL_FILL")))
DATABASE_PRINT                      = bool(strtobool(os.getenv("DATABASE_PRINT")))

DATABASE_REMOTE_SQL_HOST            = os.getenv("DATABASE_REMOTE_MYSQL_HOST")
DATABASE_REMOTE_SQL_USER            = os.getenv("DATABASE_REMOTE_MYSQL_USER")
DATABASE_REMOTE_SQL_PASSWORD        = os.getenv("DATABASE_REMOTE_MYSQL_PASSWORD")
DATABASE_REMOTE_SQL_DB              = os.getenv("DATABASE_REMOTE_MYSQL_DB")

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
        logger.info(f"_fill()")
        session = self.SessionLocal()
        try:
            self._clear()
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
            logger.error(f"_fill(): Fehler: {e}")
            raise e
        finally:
            session.close()

    def _clear(self):
        """Löscht den Inhalt der Datenbank."""
        logger.info(f"_clear()")
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
            logger.error(f"_clear(): Fehler: {e}")
            raise e
        finally:
            session.close()

    def _print(self): 
        """Printe Datenbank"""
        logger.info(f"_print()")

        def filter_instance_state(data):
            return {key: value for key, value in data.items() if key != '_sa_instance_state'}
        
        session = self.SessionLocal()
        try:
            show_tables = {
                'Slot': True,
                'Song': True,
                'Edit': True,
                'Group': True,
                'Invitation': True,
                'User': True,
                'LoginRequest': True,
                'OccupiedSlot': True
            }

            # Sammle alle Tabelleninhalte in einem String
            log_output = ""

            if show_tables.get('Slot', False):
                slots = session.execute(select(model.Slot)).scalars().all()
                slot_data = [filter_instance_state(instance.__dict__) for instance in slots]
                log_output += "\nSlot Table:\n"
                log_output += tabulate(slot_data, headers="keys", tablefmt="grid") + "\n"
            
            if show_tables.get('Song', False):
                songs = session.execute(select(model.Song)).scalars().all()
                song_data = [filter_instance_state(instance.__dict__) for instance in songs]
                log_output += "\nSong Table:\n"
                log_output += tabulate(song_data, headers="keys", tablefmt="grid") + "\n"
            
            if show_tables.get('Edit', False):
                edits = session.execute(select(model.Edit)).scalars().all()
                edit_data = [filter_instance_state(instance.__dict__) for instance in edits]
                log_output += "\nEdit Table:\n"
                log_output += tabulate(edit_data, headers="keys", tablefmt="grid") + "\n"
            
            if show_tables.get('Group', False):
                groups = session.execute(select(model.Group)).scalars().all()
                group_data = [filter_instance_state(instance.__dict__) for instance in groups]
                log_output += "\nGroup Table:\n"
                log_output += tabulate(group_data, headers="keys", tablefmt="grid") + "\n"
            
            if show_tables.get('Invitation', False):
                invitations = session.execute(select(model.Invitation)).scalars().all()
                invitation_data = [filter_instance_state(instance.__dict__) for instance in invitations]
                log_output += "\nInvitation Table:\n"
                log_output += tabulate(invitation_data, headers="keys", tablefmt="grid") + "\n"
            
            if show_tables.get('User', False):
                users = session.execute(select(model.User)).scalars().all()
                user_data = [filter_instance_state(instance.__dict__) for instance in users]
                log_output += "\nUser Table:\n"
                log_output += tabulate(user_data, headers="keys", tablefmt="grid") + "\n"
            
            if show_tables.get('LoginRequest', False):
                login_requests = session.execute(select(model.LoginRequest)).scalars().all()
                login_request_data = [filter_instance_state(instance.__dict__) for instance in login_requests]
                log_output += "\nLoginRequest Table:\n"
                log_output += tabulate(login_request_data, headers="keys", tablefmt="grid") + "\n"
            
            if show_tables.get('OccupiedSlot', False):
                occupied_slots = session.execute(select(model.OccupiedSlot)).scalars().all()
                occupied_slot_data = [filter_instance_state(instance.__dict__) for instance in occupied_slots]
                log_output += "\nOccupiedSlot Table:\n"
                log_output += tabulate(occupied_slot_data, headers="keys", tablefmt="grid") + "\n"

            # Ausgabe des gesammelten Logs in einem großen Log-Eintrag
            logger.info(log_output)

        except Exception as e:
            session.rollback()
            logger.error(f"_print(): Fehler: {e}")
            raise e
        finally:
            session.close()




"""Implementations for Different Session Managers"""
class RemoteDatabaseSessionManager(BaseDatabaseSessionManager):
    def __init__(self):
        logger.info(f"__init__(): (remote)")
        database_url = f"mysql+pymysql://{DATABASE_REMOTE_SQL_USER}:{DATABASE_REMOTE_SQL_PASSWORD}@{DATABASE_REMOTE_SQL_HOST}/{DATABASE_REMOTE_SQL_DB}"
        engine = create_engine(database_url)
        Base.metadata.create_all(bind=engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.info(f"__init__(): verbunden (remote)")

        if DATABASE_PRINT:
            self._print()

    # @contextmanager
    def get_session(self) -> Generator[Session, Any, None]:
        logger.info(f"get_session(): (remote)")
        database_session = self.SessionLocal()
        try:
            yield database_session
        finally:
            database_session.close()
            logger.info(f"get_session(): closed session (remote)")

class LocalDatabaseSessionManager(BaseDatabaseSessionManager):
    def __init__(self):
        logger.info(f"__init__(): (local)")
        os.makedirs("./outgoing/database", exist_ok=True)
        database_url = f"sqlite:///./outgoing/database/local.db"
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.info(f"__init__(): verbunden (local)")

        if DATABASE_LOCAL_FILL:
            self._fill(data)

        if DATABASE_PRINT:
            self._print()

    # @contextmanager
    def get_session(self) -> Generator[Session, Any, None]:
        logger.info(f"get_session(): (local)")
        database_session = self.SessionLocal()
        try:
            yield database_session
        finally:
            database_session.close()
            logger.info(f"get_session(): closed session (local)")

class MemoryDatabaseSessionManager(BaseDatabaseSessionManager):
    def __init__(self):
        logger.info(f"__init__(): (memory)")
        database_url = "sqlite:///:memory:"
        self.engine = create_engine(database_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        logger.info(f"__init__(): verbunden (memory)")
        self._fill(data)

    # @contextmanager
    def get_session(self) -> Generator[Session, Any, None]:
        logger.info(f"get_session(): (memory)")
        connection = self.engine.connect()
        transaction = connection.begin()
        session = self.SessionLocal(bind=connection)
        try:
            yield session
        finally:
            session.close()
            transaction.rollback()
            connection.close()
            logger.info(f"get_session(): closed session (memory)")


_database_session_manager = None

def init_database_session_manager(): 
    logger.info(f"init_database_manager()")
    
    global _database_session_manager
    if _database_session_manager is None:
        _database_session_manager = LocalDatabaseSessionManager() if DATABASE_LOCAL else RemoteDatabaseSessionManager()
    else:
        logger.warning(f"init_database_manager(): already initalized")

def get_database_session():
    logger.info(f"get_database_session()")
    
    global _database_session_manager
    if _database_session_manager is None:
        logger.error("get_database_session(): failed! manager not initilized")
        return

    try:
        gen = _database_session_manager.get_session() 
        session = next(gen)
        yield session
    except Exception as e:
        logger.error(f"get_database_session(): Fehler: {e}")
        raise e
