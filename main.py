from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from dotenv import load_dotenv
from distutils.util import strtobool
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
from test.utils.testing_data.db.fill import fill

# setup loggers
setup_logging_prod()

# env
load_dotenv()

# Define the lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    
    # Create tables
    model.Base.metadata.create_all(bind=engine)
    LOCAL_DB = strtobool(os.getenv("LOCAL_DB"))

    # Fill and print data
    with SessionLocal() as session:
        if LOCAL_DB:  # Guard
            # Only uncomment if you want to renew the data
            fill(session)
        
        print_database_contents(session, {
            'Slot':         True,
            'Song':         True,
            'Edit':         True,
            'Group':        True,
            'Invitation':   True,
            'User':         True,
            'LoginRequest': True,
            'OccupiedSlot': True
        })

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
async def root():
    return 17