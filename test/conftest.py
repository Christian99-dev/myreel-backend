import logging
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models.database.model import Base
from api.utils.database.fill_test_model import fill_test_model
from logging_config import setup_logging_testing
from ..main import app
from api.config.database import get_db

# setup logging
setup_logging_testing()

# setup test db
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ONLY DATABASE
@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session_empty(db_engine):
    """Creates a new database session for a test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
@pytest.fixture(scope="function")
def db_session_filled(db_engine):
    """Creates a new database session for a test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    fill_test_model(session)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

# FULL APP CLIENT
@pytest.fixture(scope="function")
def app_client(db_engine):
    def override_get_db_empty():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
            
    app.dependency_overrides[get_db] = override_get_db_empty
    yield TestClient(app)
    app.dependency_overrides.pop(get_db, None)

    
@pytest.fixture(scope="function")
def app_client_filled(db_engine):
    def override_get_db_filled():
        db = TestingSessionLocal()
        try:
            fill_test_model(db)
            yield db
        finally:
            db.close()