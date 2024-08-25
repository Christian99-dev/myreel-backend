from contextlib import asynccontextmanager
import os
from fastapi import Depends, FastAPI
from dotenv import load_dotenv
from distutils.util import strtobool
from api.config import media_access
from api.config.media_access import MediaAccess, get_media_access, media_dependency
from api.models.database import model
from api.utils.database.print_database_contents import print_database_contents
from logging_config import setup_logging_prod

# database
from api.config.database import get_db, engine, SessionLocal

#routes
from api.config.path_roles import path_roles
from api.routes.song import router as song_router
from api.routes.group import router as group_router

# middleware 
from api.middleware.log_access_path import LogAccessMiddleware
from api.middleware.access_handler import AccessHandlerMiddleware
from api.mock.database.fill import fill

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
            fill(session)
        
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
    # get media and fill
    yield

# app
app = FastAPI(lifespan=lifespan)

# add middleware
app.add_middleware(LogAccessMiddleware)
app.add_middleware(AccessHandlerMiddleware, path_roles=path_roles, get_db=get_db)

# router
app.include_router(song_router)
app.include_router(group_router)

# root
@app.get("/")
async def root(media_access: MediaAccess = Depends(get_media_access)):
    return 17