from fastapi import FastAPI

#routes
from api.routes.song import router as song_router
from api.routes.group import router as group_router

app = FastAPI()

app.include_router(song_router)
app.include_router(group_router)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

# uvicorn main:app --reload