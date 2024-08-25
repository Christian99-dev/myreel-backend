import pytest
import logging
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, Session
from api.models.database.model import Base, Song
from test.utils.testing_data.db.fill import fill
from logging_config import setup_logging_testing
from api.routes.song import router as song_router
from api.routes.group import router as group_router
from api.config.database import get_db, get_db_memory

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
    
    
# ----------------------------------------------------NEW------------------------------------------------------------------------------------------

## -- MAIN FIXTURES -- ## 

# Database   : Test_Data 
# Routes     : None
# Middleware : None
@pytest.fixture(scope="function")
def db_memory():
    session_generator = get_db_memory()  
    session = next(session_generator)
    fill(session)   
    yield session


# Database   : Test_Data 
# Routes     : Prod
# Middleware : None 
@pytest.fixture(scope="function")
def http_client(db_memory):
    
    # adding prod routes
    app = FastAPI()
    app.include_router(group_router)
    app.include_router(song_router)
    @app.get("/")
    async def root():
        return 17
    
    def get_db_override():
        yield db_memory

    # Überschreibe die get_db-Abhängigkeit
    app.dependency_overrides[get_db] = get_db_override

    with TestClient(app) as test_client:
        yield test_client

    # Entferne die Überschreibung nach dem Test
    del app.dependency_overrides[get_db]

## -- SPECIFIC FIXTURES -- ## 

# Database   : Test_Data 
# Routes     : Mocked
# Middleware : None  
# Descriptsion : 
# 
# This is mainly for testing the behavoiur of a roundtrip from route to service to database, 
# if no routes in prod are available. so we are just mocking crud operations.
@pytest.fixture(scope="function")
def http_client_mocked_crud(db_memory):
    # fresh client
    app = FastAPI()
    
    # CRUD routes for songs
    @app.post("/add/{name}/{author}")
    async def add(name: str, author: str, db: Session = Depends(lambda: db_memory)):
        new_song = Song(name=name, author=author, times_used=0, cover_src="cover_src", audio_src="audio_src")
        db.add(new_song)
        db.commit()
        db.refresh(new_song)
        return new_song

    @app.get("/list")
    async def list(db: Session = Depends(lambda: db_memory)):
        return db.query(Song).all()
    
    # yield client with routes
    with TestClient(app) as test_client:
        yield test_client