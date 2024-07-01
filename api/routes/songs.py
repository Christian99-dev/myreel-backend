from fastapi import APIRouter, HTTPException
from api.models.routes.songs import CreateRequest, CreateResponse
from api.services.songs import create as createService
from api.config.database import db_dependency


router = APIRouter(
    prefix="/songs",
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
        return CreateResponse(message=f"Song '{new_song.name}' by '{new_song.author}' created successfully", song=new_song)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))