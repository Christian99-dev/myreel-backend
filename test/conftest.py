import os

import pytest
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.config.endpoints import endpoint_config
from api.config.exceptions import add_exception_handlers
from api.middleware.access_handler import AccessHandlerMiddleware
from api.routes.edit import router as edit_router
from api.routes.group import router as group_router
from api.routes.song import router as song_router
from api.routes.user import router as user_router
from api.sessions.database import (MemoryDatabaseSessionManager,
                                   get_database_session)
from api.sessions.email import MemoryEmailSessionManager, get_email_session
from api.sessions.files import MemoryFileSessionManager, get_file_session
from api.sessions.instagram import (MemoryInstagramSessionManager,
                                    get_instagram_session)
from api.utils.jwt import jwt
from logging_config import setup_logging

# env
load_dotenv()

"""Logger"""
@pytest.fixture(scope="session", autouse=True)
def setup_test_logging():
    setup_logging(env="test")

"""Creds"""
@pytest.fixture(scope="session")
def admintoken():
    return os.getenv("ADMIN_TOKEN")

@pytest.fixture(scope="session")
def bearer_headers():
    return [
        {"Authorization": f"Bearer {jwt.create_jwt(1, 30)}"},
        {"Authorization": f"Bearer {jwt.create_jwt(2, 30)}"},
        {"Authorization": f"Bearer {jwt.create_jwt(3, 30)}"},
    ]
    
"""Database"""
@pytest.fixture(scope="function")
def memory_database_session():
    memory_database_session_manager = MemoryDatabaseSessionManager()
    yield from memory_database_session_manager.get_session()

"""Files"""    
@pytest.fixture(scope="function")
def memory_file_session():
    memory_file_session_manager = MemoryFileSessionManager()
    yield from memory_file_session_manager.get_session()

"""Email"""
@pytest.fixture(scope="function")
def memory_instagram_session():
    memory_instagram_session_manager = MemoryInstagramSessionManager()
    yield from memory_instagram_session_manager.get_session()

"""Instagram"""
@pytest.fixture(scope="function")
def memory_email_session():
    memory_email_session_manager = MemoryEmailSessionManager()
    yield from memory_email_session_manager.get_session()

"""HTTP Client"""
@pytest.fixture(scope="function")
def http_client(
        memory_database_session     : Session, 
        memory_file_session         : MemoryFileSessionManager, 
        memory_instagram_session    : MemoryInstagramSessionManager, 
        memory_email_session         : MemoryEmailSessionManager
    ):
    
    # adding prod routes
    app = FastAPI()
    app.include_router(song_router)
    app.include_router(group_router)
    app.include_router(user_router)
    app.include_router(edit_router)

    # add exception handler 
    add_exception_handlers(app)
    
    # override sessions
    def get_database_session_override():
        yield memory_database_session


    def get_instagram_session_override():
        yield memory_instagram_session


    def get_email_session_override():
        yield memory_email_session


    def get_file_session_override():
        yield memory_file_session
    
    # adding middleware
    app.add_middleware(AccessHandlerMiddleware, endpoint_config=endpoint_config, get_database_session=get_database_session_override)
    
    # Überschreibe die get_xxx_session-Abhängigkeit
    app.dependency_overrides[get_database_session] = get_database_session_override
    app.dependency_overrides[get_file_session] = get_file_session_override
    app.dependency_overrides[get_instagram_session] = get_instagram_session_override
    app.dependency_overrides[get_email_session] = get_email_session_override

    with TestClient(app) as test_client:
        yield test_client
        
    del app.dependency_overrides[get_database_session]
    del app.dependency_overrides[get_file_session]
    del app.dependency_overrides[get_instagram_session]
    del app.dependency_overrides[get_email_session]
        