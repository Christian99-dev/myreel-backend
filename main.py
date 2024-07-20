from fastapi import FastAPI

#routes
from api.routes.song import router as song_router
from api.routes.group import router as group_router

# middleware 
from api.middleware.log_access_path import LogAccessMiddleware

# app
app = FastAPI()

# add middleware
app.add_middleware(LogAccessMiddleware)

# router
app.include_router(song_router)
app.include_router(group_router)

# root
@app.get("/")
async def root():
    return 17