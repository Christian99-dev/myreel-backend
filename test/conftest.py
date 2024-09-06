import os
import pytest
import logging
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from api.sessions.database import MemoryDatabaseSessionManager
from api.utils.jwt import jwt
from api.config.endpoints import path_config
from api.sessions.email import BaseEmailAccess, MemoryEmailAcccess, get_email_access
from api.sessions.instagram import BaseInstagramAccess, MemoryInstagramAcccess, get_instagram_access
from api.sessions.files import BaseMediaAccess, MemoryMediaAccess, get_media_access
from api.middleware.access_handler import AccessHandlerMiddleware
from api.models.database.model import Song
from api.utils.routes.extract_role_credentials_from_request import extract_role_credentials_from_request
from logging_config import setup_logging_testing
from api.routes.song import router as song_router
from api.routes.group import router as group_router
from api.routes.user import router as user_router
from api.routes.edit import router as edit_router
from api.security.endpoints_class import EndpointConfig, EndpointInfo
from api.security.role_enum import RoleEnum
from api.sessions.database import database_session_manager
# setup logging
setup_logging_testing()
logger = logging.getLogger("testing")

# env
load_dotenv()


## -- MAIN FIXTURES -- ## 

# Database   : None 
# Media      : None
# Routes     : None
# Middleware : None
@pytest.fixture(scope="function")
def user_1_jwt():
    yield jwt.create_jwt(1, 10)
    
# Database   : None 
# Media      : None
# Routes     : None
# Middleware : None
@pytest.fixture(scope="function")
def admintoken():
    yield os.getenv("ADMIN_TOKEN")
    
# Database   : Test_Data 
# Media      : None
# Routes     : None
# Middleware : None
@pytest.fixture(scope="function")
def db_memory():
    memory_database_session_manager = MemoryDatabaseSessionManager()
    with memory_database_session_manager.get_session() as session:
        yield session 
    
# Database   : None
# Media      : Mock Media
# Routes     : None
# Middleware : None
@pytest.fixture
def media_access_memory():
    media_access_memory = MemoryMediaAccess()
    media_access_memory.fill("mock/files")
    return media_access_memory

# Database   : None
# Media      : None
# Routes     : None
# Middleware : None
@pytest.fixture
def instagram_access_memory():
    return MemoryInstagramAcccess()

# Database   : None
# Media      : None
# Routes     : None
# Middleware : None
@pytest.fixture
def email_access_memory():
    return MemoryEmailAcccess()


# Database   : Test_Data
# Media      : None 
# Routes     : Prod
# Middleware : None 
@pytest.fixture(scope="function")
def http_client(
        db_memory: Session, 
        media_access_memory: MemoryMediaAccess, 
        instagram_access_memory: MemoryInstagramAcccess, 
        email_access_memory: MemoryEmailAcccess
    ):
    
    # adding prod routes
    app = FastAPI()
    app.include_router(song_router)
    app.include_router(group_router)
    app.include_router(user_router)
    app.include_router(edit_router)
    
    def get_db_override():
        yield db_memory
        
    def get_instagram_access_override():
        return instagram_access_memory

    def get_email_access_override():
        return email_access_memory

    def get_media_access_override():
        return media_access_memory
    
    # adding middleware
    app.add_middleware(AccessHandlerMiddleware, path_config=path_config, get_db=get_db_override)
    
    

    # Überschreibe die get_db-Abhängigkeit
    app.dependency_overrides[database_session_manager.get_session] = get_db_override
    app.dependency_overrides[get_instagram_access] = get_instagram_access_override
    app.dependency_overrides[get_email_access] = get_email_access_override
    app.dependency_overrides[get_media_access] = get_media_access_override

    with TestClient(app) as test_client:
        yield test_client
        
    del app.dependency_overrides[database_session_manager.get_session]
    del app.dependency_overrides[get_instagram_access]
    del app.dependency_overrides[get_email_access]
    del app.dependency_overrides[get_media_access]
    

## -- SPECIFIC FIXTURES -- ## 

# Database   : Test_Data 
# Media      : None
# Routes     : add and list
# Middleware : None  
# Description : 
# 
# This is mainly for testing the behavoiur of a roundtrip from route to service to database, 
# if no routes in prod are available. so we are just mocking crud operations.
@pytest.fixture(scope="function")
def http_client_mocked_path_crud(db_memory: Session):
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
        
# Database   : Test_Data 
# Media      : None
# Routes     : for every mocked path one
# Middleware : Access_Handler  
# Description : 
# 
# A fixture where every possible role is has a dedicated path, to test out security access in a non prod env
@pytest.fixture(scope="function")
def http_client_mocked_path_config(db_memory: Session):
    
    # simulating prod api
    app = FastAPI()
    
    # session
    def get_db_override(): 
        yield db_memory
        
    mock_path_config = EndpointConfig({
    '/admin_no_subroles': {
        "GET": EndpointInfo(role=RoleEnum.ADMIN, has_subroles=False),
    },
    '/group_creator_no_subroles': {
        "GET": EndpointInfo(role=RoleEnum.GROUP_CREATOR, has_subroles=False),
    },
    '/edit_creator_no_subroles': {
        "GET": EndpointInfo(role=RoleEnum.EDIT_CREATOR, has_subroles=False),
    },
    '/group_member_no_subroles': {
        "GET": EndpointInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=False),
    },
    '/external_no_subroles': {
        "GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=False),
    },
    '/admin_subroles': {
        "GET": EndpointInfo(role=RoleEnum.ADMIN, has_subroles=True),
    },
    '/group_creator_subroles': {
        "GET": EndpointInfo(role=RoleEnum.GROUP_CREATOR, has_subroles=True),
    },
    '/edit_creator_subroles': {
        "GET": EndpointInfo(role=RoleEnum.EDIT_CREATOR, has_subroles=True),
    },
    '/group_member_subroles': {
        "GET": EndpointInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True),
    },
    '/external_subroles': {
        "GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True),
    },
})
    
    # middleware for access testing 
    app.add_middleware(AccessHandlerMiddleware, path_config=mock_path_config, get_db=get_db_override)
    
    # every endpoints based on testconfig file
    def create_endpoint(m_name: str):
        async def endpoint(request: Request):
            return f"You called {m_name}"
        return endpoint

    for path, method in mock_path_config.get_all_paths_and_methods():
        app.add_api_route(f"{path}", create_endpoint(path), methods=[method])
    
    # yield client with routes
    with TestClient(app) as test_client:
        yield test_client
        
# Database   : Test_Data 
# Media      : None
# Routes     : for body and path params
# Middleware : extracing credentials  
# Description : 
# 
# A client where i can test putting in credetials in routes (params, body, path) and extracing them in the middleware
@pytest.fixture(scope="function")
def http_client_mocked_path_for_extracting_creds():
    app = FastAPI()

    @app.middleware("http")
    async def add_role_credentials(request: Request, call_next):
        credentials = await extract_role_credentials_from_request(request)
        request.state.credentials = credentials
        response = await call_next(request)
        return response

    # from body / query
    @app.get("/example")
    async def example_route(request: Request):
        return {"credentials": request.state.credentials}
    
    @app.post("/example")
    async def example_route(request: Request):
        return {"credentials": request.state.credentials}

    # from path
    @app.post("/group/{groupid}")
    async def group_route(request: Request, groupid: str):
        return {"credentials": request.state.credentials}

    @app.post("/edit/{editid}")
    async def edit_route(request: Request, editid: int):
        return {"credentials": request.state.credentials}
    
    @app.post("/example/group/{groupid}/example")
    async def nested_group_route(request: Request, groupid: str):
        return {"credentials": request.state.credentials}

    @app.post("/example/edit/{editid}/example")
    async def nested_edit_route(request: Request, editid: int):
        return {"credentials": request.state.credentials}
    
    # yield client with routes
    with TestClient(app) as test_client:
        yield test_client