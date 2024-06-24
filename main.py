from fastapi import FastAPI, HTTPException, Depends,status
from pydantic import BaseModel
from typing import Annotated
from api.config.database import engine, get_db
from sqlalchemy.orm import Session

import api.models.models as models

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

db_dependency = Annotated[Session, Depends(get_db)]

# uvicorn main:app --reload