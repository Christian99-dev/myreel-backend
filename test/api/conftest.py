import logging
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models.database.model import Base
from api.utils.database.fill_test_model import fill_test_model

# Set up the test database URL
DATABASE_URL = "sqlite:///:memory:"

# Create a new database engine for the test database
engine = create_engine(DATABASE_URL, echo=False)  # Set echo=False to reduce logs

class MyFilter(object):
    def __init__(self, level):
        self.__level = level

    def filter(self, logRecord):
        return logRecord.levelno <= self.__level

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)
logging.getLogger("testing").addFilter(MyFilter(logging.DEBUG))

# Create a configured "Session" class
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    yield engine
    # Drop the database tables
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
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

