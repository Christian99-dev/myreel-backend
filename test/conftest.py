import pytest
import logging
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from api.middleware.access_handler import AccessHandlerMiddleware
from api.models.database.model import Base
from test.utils.mock_path_roles import mock_path_roles
from test.utils.fill_test_model import fill_test_model
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
    fill_test_model(session)
    
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
    
# routes        = mock_path_roles mirrored
# database      = test_model
# middleware    yes
@pytest.fixture(scope="function")
def app_client_mock_routes_middleware(db_session_filled):
    def override_get_db():
        yield db_session_filled

    # simulating prod api
    app = FastAPI()
    
    # middleware for access testing 
    app.add_middleware(AccessHandlerMiddleware, path_roles=mock_path_roles, get_db=override_get_db)
    
    # every endpoints based on testconfig file
    def create_endpoint(m_name: str):
        async def endpoint(request: Request):
            return f"You called {m_name}"
        return endpoint

    for path in mock_path_roles.keys():    
        app.add_api_route(f"{path}", create_endpoint(path), methods=["GET"])
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)
    
    app.dependency_overrides.pop(get_db, None)
