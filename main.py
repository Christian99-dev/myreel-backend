from fastapi import FastAPI

#routes
from api.routes.song import router as song_router

app = FastAPI()

app.include_router(song_router)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

# uvicorn main:app --reload