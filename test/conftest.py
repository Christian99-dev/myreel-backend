import pytest
import logging
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from api.models.database.model import Base
from test.utils.testing_data.db.fill import fill
from logging_config import setup_logging_testing
from api.routes.song import router as song_router
from api.routes.group import router as group_router
from api.config.database import get_db

# setup logging
setup_logging_testing()
logger = logging.getLogger("testing")

# setup test db
engine = create_engine("sqlite:///:memory:", 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# -- DB ENGINE -- #
@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


# -- DB SESSIONS -- #

# database = none
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

# database = test_model
@pytest.fixture(scope="function")
def db_session_filled(db_engine):
    """Creates a new database session for a test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    fill(session)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

# -- HTTP CLIENTS -- #

# routes        = none
# database      = none
# middleware    no
@pytest.fixture(scope="function")
def app_client_empty(): 
    yield TestClient(FastAPI())

# routes        = prod mirrored
# database      = test_model
# middleware    no
@pytest.fixture(scope="function")
def app_client_prod_routes(db_session_filled):
    
    # simulating prod api
    app = FastAPI()
    app.include_router(group_router)
    app.include_router(song_router)
    @app.get("/")
    async def root():
        return 17
    
    def override_get_db():
        yield db_session_filled
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.pop(get_db, None)