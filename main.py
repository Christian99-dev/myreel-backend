from contextlib import asynccontextmanager
import os
from fastapi import APIRouter, Depends, FastAPI
from dotenv import load_dotenv
from distutils.util import strtobool
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from api.models.database import model
from api.utils.database.print_database_contents import print_database_contents
from logging_config import setup_logging_prod
from api.auth.path_config import path_config
# media 
from api.mock.media.fill import fill as fill_media
from api.config.media_access import BaseMediaAccess, media_access

# database
from api.config.database import engine, SessionLocal, get_db
from api.mock.database.fill import fill as fill_db
from api.mock.database.model import mock_model_local_links

#routes
from api.routes.song import router as song_router
from api.routes.static import router as static_router
from api.routes.testing import router as testing_router
from api.routes.group import router as group_router
from api.routes.user import router as user_router

# middleware 
from api.middleware.log_access_path import LogAccessMiddleware
from api.middleware.access_handler import AccessHandlerMiddleware

# setup loggers
setup_logging_prod()

# env
load_dotenv()

# Define the lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    
    # Database setup and fill if neede
    model.Base.metadata.create_all(bind=engine)
    LOCAL_DB = strtobool(os.getenv("LOCAL_DB"))
    with SessionLocal() as session:
        if LOCAL_DB:  # Guard
            # Only uncomment if you want to renew the data
            # fill_db(session, mock_model_local_links)
            pass
        
        print_database_contents(session, {
            'Slot':         False,
            'Song':         False,
            'Edit':         False,
            'Group':        True,
            'Invitation':   False,
            'User':         True,
            'LoginRequest': True,
            'OccupiedSlot': False
        })

    # Media setup and fill if neede
    # fill_media(media_access)
    yield

# app
app = FastAPI(lifespan=lifespan)

# add middleware
app.add_middleware(LogAccessMiddleware)
app.add_middleware(AccessHandlerMiddleware, path_config=path_config, get_db=get_db)

# router
app.include_router(testing_router)
app.include_router(static_router)
app.include_router(song_router)
app.include_router(group_router)
app.include_router(user_router)


# root
@app.get("/")
async def root():
    return 17


