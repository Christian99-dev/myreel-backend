from fastapi import FastAPI
from logging_config import setup_logging_prod
from api.config.database import get_db

#routes
from api.config.path_roles import path_roles
from api.routes.song import router as song_router
from api.routes.group import router as group_router

# middleware 
from api.middleware.log_access_path import LogAccessMiddleware
from api.middleware.access_handler import AccessHandlerMiddleware

# setup loggers
setup_logging_prod()

# app
app = FastAPI()

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