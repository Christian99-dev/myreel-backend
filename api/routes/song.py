from fastapi import APIRouter, HTTPException
from api.models.schema.song import CreateRequest, CreateResponse
from api.services.song import create as createService
from api.config.database import db_dependency


router = APIRouter(
    prefix="/song",
)    

@router.post("/create", response_model=CreateResponse)
def create(request: CreateRequest, db: db_dependency) -> CreateResponse:
    try:
        new_song = createService(
            request.name, 
            request.author, 
            request.cover_src, 
            request.audio_src, 
            db
        )
        return CreateResponse.from_orm(new_song)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.delete("/delete")
def delete(id: int, db: db_dependency):
    return

@router.patch("/update")
def update(id: int, db: db_dependency):
    return

@router.get("/get")
def get(id: int, db: db_dependency):
    return

@router.get("/list")
def list(db: db_dependency):
    return