from fastapi import APIRouter, Depends, HTTPException
from api.models.schema.song import CreateRequest, CreateResponse, GetResponse, ListResponse
from api.services.database.song import create as create_service, list_all as list_all_service, get as get_service
from api.config.database import Session, get_db
#TODO SONG
router = APIRouter(
    prefix="/song",
)    

# @router.post("/create", response_model=CreateResponse, tags=["song"])
# async def create(request: CreateRequest, db: Session = Depends(get_db)) -> CreateResponse:
#     try:
#         new_song = create_service(
#             request.name, 
#             request.author, 
#             request.cover_src, 
#             request.audio_src, 
#             db
#         )
#         return new_song
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
    
# @router.delete("/delete")
# def delete(id: int, db: Session = Depends(get_db)):
#     return

# @router.patch("/update")
# def update(id: int, db: Session = Depends(get_db)):
#     return

# @router.get("/get/{song_id}", response_model=GetResponse, tags=["song"])
# async def get(song_id: int, db: Session = Depends(get_db)) -> GetResponse:
#     song = get_service(song_id, db)
#     if song is None:
#         raise HTTPException(status_code=404, detail="Song not found")
#     return song


# @router.get("/list", response_model=ListResponse, tags=["song"])
# async def list_all(db: Session = Depends(get_db)) -> ListResponse:
#     try:
#         songs = list_all_service(db)    
#         return {"songs": songs}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))