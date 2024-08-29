from fastapi import APIRouter, Depends, HTTPException
from api.models.schema.song import DeleteResponse, GetResponse, ListResponse, PostRequest, PostResponse

# sessions
from api.config.media_access import get_media_access, BaseMediaAccess
from api.config.database import Session, get_db

# database
from api.services.database.song import create as create_song_service, update as update_song_service, create_slots_from_breakpoints, remove as remove_song_service, get as get_song_service, list_all

# media_service
from api.services.media.song  import create as create_song_media_service, remove as remove_song_media_service
from api.services.media.cover import create as create_cover_media_service, remove as remove_cover_media_service
from api.utils.files.file_validation import file_validation
from api.utils.files.get_audio_duration import get_audio_duration

router = APIRouter(
    prefix="/song",
)    

@router.post("/", response_model=PostResponse, tags=["song"])
async def create(
    request: PostRequest = Depends(),
    db: Session = Depends(get_db),
    media_access: BaseMediaAccess = Depends(get_media_access)
):    
    try:
        if(len(request.breakpoints) < 2):
            raise HTTPException(status_code=422, detail="Not enough breakpoints")
                
        breakpoints = sorted(request.breakpoints)
        
        # validate files 
        (validated_song_file, message_song_file) = file_validation(request.song_file, "audio")
        (validated_cover_file, message_cover_file) = file_validation(request.cover_file, "image")
        

        if validated_song_file is None:
            raise HTTPException(status_code=400, detail=message_song_file)
        
        if validated_cover_file is None:
            raise HTTPException(status_code=400, detail=message_cover_file)
        
        # check if last breakpoint is not longer then the song itssleft
        song_duration = get_audio_duration(validated_song_file, "wav")
        
        if song_duration < breakpoints[-1]:
            raise HTTPException(status_code=400, detail="breakpoints exceed songduration")
        
        # Lesen der Mediendatei und der Coverdatei aus dem Request
        song_file_bytes = await validated_song_file.read()  # Mediendatei lesen
        song_extension = validated_song_file.filename.split(".")[-1]
        
        cover_file_bytes = await validated_cover_file.read()  # Coverdatei lesen
        cover_extension = validated_cover_file.filename.split(".")[-1]

        # Song in die Datenbank einfügen
        new_song = create_song_service(
            name=request.name,
            author=request.author,
            cover_src="",  # Zunächst leer, wird später gesetzt
            audio_src="",  # Zunächst leer, wird später gesetzt
            db_session=db
        )

        # save song
        song_location = create_song_media_service(new_song.song_id, song_extension, song_file_bytes, media_access)

        # save cover
        cover_location = create_cover_media_service(new_song.song_id, cover_extension, cover_file_bytes, media_access)

        # Update den Song mit den Speicherorten für Audio und Cover
        updated_song = update_song_service(
            song_id=new_song.song_id,
            cover_src=cover_location,
            audio_src=song_location,
            db_session=db
        )
        
        # create slots from breakpoints
        create_slots_from_breakpoints(new_song.song_id, breakpoints, db_session=db)
        
        if not updated_song:
            raise HTTPException(status_code=500, detail="Song not found during update.")

        # Rückgabe des erstellten und aktualisierten Songs
        return updated_song
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))    
    
@router.delete("/{song_id}", response_model=DeleteResponse, tags=["song"])
async def delete(song_id: int, db: Session = Depends(get_db), media_access: BaseMediaAccess = Depends(get_media_access)):
    # Try to remove the media file associated with the song
    song_media_removed = remove_song_media_service(song_id, media_access)
    cover_media_removed = remove_cover_media_service(song_id, media_access)
    
    # Try to remove the song from the database
    song_entry_removed = remove_song_service(song_id, db)

    # Check if any of the deletions failed
    if not song_entry_removed and not song_media_removed and not cover_media_removed:
        raise HTTPException(status_code=404, detail="Song and media not found")
    elif not song_entry_removed:
        raise HTTPException(status_code=404, detail="Song not found")
    elif not song_media_removed and not cover_media_removed:
        raise HTTPException(status_code=500, detail="Media files could not be deleted")

    return {"message": "Song and associated media deleted successfully"}

@router.get("/list", response_model=ListResponse, tags=["song"])
async def list_songs(db: Session = Depends(get_db)):
    songs = list_all(db_session=db)
    return {"songs": songs}

@router.get("/{song_id}", response_model=GetResponse, tags=["song"])
async def get(song_id: int, db: Session = Depends(get_db)):
    song = get_song_service(song_id=song_id, db_session=db)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song

