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
from api.sessions.email import MemoryEmailSessionManager, get_email_session
from api.sessions.instagram import MemoryInstagramSessionManager, get_instagram_session
from api.sessions.files import MemoryFileSessionManager, get_file_session
from api.middleware.access_handler import AccessHandlerMiddleware
from api.models.database.model import Song
from api.utils.routes.extract_role_credentials_from_request import extract_role_credentials_from_request
from logging_config import setup_logging
from api.routes.song import router as song_router
from api.routes.group import router as group_router
from api.routes.user import router as user_router
from api.routes.edit import router as edit_router
from api.security.endpoints_class import EndpointConfig, EndpointInfo
from api.security.role_enum import RoleEnum
from api.sessions.database import get_database_session

# env
load_dotenv()

"""Logger"""
@pytest.fixture(scope="session", autouse=True)
def setup_test_logging():
    setup_logging(env="test")
    
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
    

    def get_database_session_override():
        yield memory_database_session


    def get_instagram_session_override():
        yield memory_instagram_session


    def get_email_session_override():
        yield memory_email_session


    def get_file_session_override():
        yield memory_file_session
    
    # adding middleware
    app.add_middleware(AccessHandlerMiddleware, path_config=path_config, get_database_session=get_database_session_override)
    
    # Überschreibe die get_database_session-Abhängigkeit
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
        