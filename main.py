import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from api.config.endpoints import endpoint_config
from api.config.exceptions import add_exception_handlers
from api.middleware.access_handler import AccessHandlerMiddleware
from api.routes.edit import router as edit_router
from api.routes.group import router as group_router
from api.routes.song import router as song_router
from api.routes.static import router as static_router
from api.routes.testing import router as testing_router
from api.routes.slot import router as slot_router
from api.routes.user import router as user_router
from api.routes.websockets import router as websocket_router
from api.sessions.database import (get_database_session,
                                   init_database_session_manager)
from api.sessions.email import init_email_session_manager
from api.sessions.files import init_file_session_manager
from api.sessions.instagram import init_instagram_session_manager
from logging_config import setup_logging

# env
load_dotenv()
LOGGER_ENV = os.getenv("LOGGER_ENV")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database_session_manager()
    init_email_session_manager()
    init_instagram_session_manager()
    init_file_session_manager()
    yield

# setup loggers
setup_logging(env=LOGGER_ENV)

# Verwende die Lifespan-Funktion in der FastAPI-App
app = FastAPI(lifespan=lifespan)

# add middleware
app.add_middleware(AccessHandlerMiddleware, endpoint_config=endpoint_config, get_database_session=get_database_session)

# add exception handler
add_exception_handlers(app)

# router
app.include_router(testing_router)
app.include_router(static_router)
app.include_router(song_router)
app.include_router(group_router)
app.include_router(user_router)
app.include_router(edit_router)
app.include_router(slot_router)

# websockets
app.include_router(websocket_router)


# root
@app.get("/")
async def root():
    return 17


