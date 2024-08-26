from contextlib import asynccontextmanager
import os
from fastapi import Depends, FastAPI
from dotenv import load_dotenv
from distutils.util import strtobool
from fastapi.staticfiles import StaticFiles
from api.models.database import model
from api.utils.database.print_database_contents import print_database_contents
from logging_config import setup_logging_prod

# media 
from api.mock.media.fill import fill as fill_media
from api.config.media_access import media_access

# database
from api.config.database import engine, SessionLocal, get_db
from api.mock.database.fill import fill as fill_db

#routes
from api.config.path_roles import path_roles
from api.routes.song import router as song_router
from api.routes.group import router as group_router

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
            # fill_db(session)
            pass
        
        print_database_contents(session, {
            'Slot':         False,
            'Song':         False,
            'Edit':         False,
            'Group':        False,
            'Invitation':   False,
            'User':         False,
            'LoginRequest': False,
            'OccupiedSlot': False
        })

    # Media setup and fill if neede
    # fill_media(media_access)
    yield

# app
app = FastAPI(lifespan=lifespan)

# Statisches Verzeichnis einbinden
app.mount("/static", StaticFiles(directory="static"), name="static")

# add middleware
app.add_middleware(LogAccessMiddleware)
app.add_middleware(AccessHandlerMiddleware, path_roles=path_roles, get_db=get_db)

# router
app.include_router(song_router)
app.include_router(group_router)

# root
@app.get("/")
async def root():
    return 17