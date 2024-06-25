from fastapi import FastAPI

#routes
from api.routes.songs import router as songs_router

app = FastAPI()

app.include_router(songs_router)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

# uvicorn main:app --reload