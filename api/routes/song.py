from fastapi import APIRouter, HTTPException
from api.models.schema.song import CreateRequest, CreateResponse, GetResponse, ListResponse
from api.services.song import create as create_service, list_all as list_all_service, get as get_service
from api.config.database import db_dependency

# TODO get und list routes testing und schema

router = APIRouter(
    prefix="/song",
)    

@router.post("/create", response_model=CreateResponse)
async def create(request: CreateRequest, db: db_dependency) -> CreateResponse:
    try:
        new_song = create_service(
            request.name, 
            request.author, 
            request.cover_src, 
            request.audio_src, 
            db
        )
        return new_song
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# @router.delete("/delete")
# def delete(id: int, db: db_dependency):
#     return

# @router.patch("/update")
# def update(id: int, db: db_dependency):
#     return

@router.get("/get/{song_id}", response_model=GetResponse)
async def get(song_id: int, db: db_dependency) -> GetResponse:
    song = get_service(song_id, db)
    if song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return song


@router.get("/list", response_model=ListResponse)
async def list_all(db: db_dependency) -> ListResponse:
    try:
        songs = list_all_service(db)
        return {"songs": songs}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))