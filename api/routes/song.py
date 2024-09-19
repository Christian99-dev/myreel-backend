from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.models.schema.song import (DeleteResponse, GetResponse, ListResponse,
                                    PostRequest, PostResponse)
from api.services.database.song import create as create_song_service
from api.services.database.song import create_slots_from_breakpoints
from api.services.database.song import get as get_song_service
from api.services.database.song import list_all
from api.services.database.song import remove as remove_song_service
from api.services.database.song import update as update_song_service
from api.services.files.cover import create as create_cover_media_service
from api.services.files.cover import remove as remove_cover_media_service
from api.services.files.song import create as create_song_media_service
from api.services.files.song import remove as remove_song_media_service
from api.sessions.database import get_database_session
from api.sessions.files import BaseFileSessionManager, get_file_session
from api.utils.files.file_validation import file_validation
from api.utils.files.get_audio_duration import get_audio_duration

router = APIRouter(
    prefix="/song",
)    

@router.post("/", response_model=PostResponse, tags=["song"])
async def create(
    request: PostRequest = Depends(),
    database_session: Session = Depends(get_database_session),
    file_session: BaseFileSessionManager = Depends(get_file_session)
):    
    try:
        if(len(request.breakpoints) < 2):
            raise HTTPException(status_code=422, detail="Not enough breakpoints")
                
        breakpoints = sorted(request.breakpoints)
        
        # validate files 
        validated_song_file = file_validation(request.song_file, "audio")
        validated_cover_file = file_validation(request.cover_file, "image")
        
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
            database_session=database_session
        )

        # save song
        song_location = create_song_media_service(new_song.song_id, song_extension, song_file_bytes, file_session)

        # save cover
        cover_location = create_cover_media_service(new_song.song_id, cover_extension, cover_file_bytes, file_session)

        # Update den Song mit den Speicherorten für Audio und Cover
        updated_song = update_song_service(
            song_id=new_song.song_id,
            cover_src=cover_location,
            audio_src=song_location,
            database_session=database_session
        )
        
        # create slots from breakpoints
        create_slots_from_breakpoints(new_song.song_id, breakpoints, database_session=database_session)
        
        if not updated_song:
            raise HTTPException(status_code=500, detail="Song not found during update.")

        # Rückgabe des erstellten und aktualisierten Songs
        return updated_song
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))    
    
@router.delete("/{song_id}", response_model=DeleteResponse, tags=["song"])
async def delete(song_id: int, database_session: Session = Depends(get_database_session), file_session: BaseFileSessionManager = Depends(get_file_session)):
    # Try to remove the media file associated with the song
    song_media_removed = remove_song_media_service(song_id, file_session)
    cover_media_removed = remove_cover_media_service(song_id, file_session)
    
    # Try to remove the song from the database
    song_entry_removed = remove_song_service(song_id, database_session)

    # Check if any of the deletions failed
    if not song_entry_removed and not song_media_removed and not cover_media_removed:
        raise HTTPException(status_code=404, detail="Song and media not found")
    elif not song_entry_removed:
        raise HTTPException(status_code=404, detail="Song not found")
    elif not song_media_removed and not cover_media_removed:
        raise HTTPException(status_code=500, detail="Media files could not be deleted")

    return {"message": "Song and associated media deleted successfully"}

@router.get("/list", response_model=ListResponse, tags=["song"])
async def list_songs(database_session: Session = Depends(get_database_session)):
    songs = list_all(database_session=database_session)
    return {"songs": songs}

@router.get("/{song_id}", response_model=GetResponse, tags=["song"])
async def get(song_id: int, database_session: Session = Depends(get_database_session)):
    song = get_song_service(song_id=song_id, database_session=database_session)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song

