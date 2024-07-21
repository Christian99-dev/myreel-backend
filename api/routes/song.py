from fastapi import APIRouter, Depends, HTTPException
from api.models.database.model import Song
from api.models.schema.song import CreateRequest, CreateResponse
from api.services.song import create as createService
from api.config.database import db_dependency, get_db

# TODO create endpoint testen
# TODO get und list routes testing und schema

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
        return new_song
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# @router.delete("/delete")
# def delete(id: int, db: db_dependency):
#     return

# @router.patch("/update")
# def update(id: int, db: db_dependency):
#     return

# @router.get("/get/{song_id}", response_model=Song)
# async def get(song_id: int, db: Session = Depends(get_db)):
#     song = get(song_id, db)
#     if song is None:
#         raise HTTPException(status_code=404, detail="Song not found")
#     return song

# @router.get("/list", response_model=list[Song])
# async def list(db: Session = Depends(get_db)):
#     return list(db)