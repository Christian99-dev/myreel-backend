from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.models.schema.song import (DeleteResponse, GetResponse, ListResponse,
                                    PostRequest, PostResponse)
from api.services.database.song import create as create_song_database
from api.services.database.song import create_slots_from_breakpoints as create_slots_from_breakpoints_database
from api.services.database.song import get as get_song_database
from api.services.database.song import list_all as list_all_songs_database
from api.services.database.song import remove as remove_song_database
from api.services.database.song import update as update_song_database
from api.services.files.cover import create as create_cover_files
from api.services.files.cover import remove as remove_cover_files
from api.services.files.song import create as create_song_files
from api.services.files.song import remove as remove_song_files
from api.sessions.database import get_database_session
from api.sessions.files import BaseFileSessionManager, get_file_session
from api.utils.files.file_validation import file_validation
from api.utils.files.get_audio_duration import get_audio_duration

router = APIRouter(
    prefix="/song",
)    

@router.post("/", response_model=PostResponse)
async def create_song(
    request: PostRequest = Depends(),
    database_session: Session = Depends(get_database_session),
    file_session: BaseFileSessionManager = Depends(get_file_session)
):
    breakpoints = request.breakpoints

    # Validate and read files
    validated_song_file = file_validation(request.song_file, "audio")
    validated_cover_file = file_validation(request.cover_file, "image")

    # Validate breakpoints against song duration
    song_duration = get_audio_duration(validated_song_file, "wav")
    if song_duration < breakpoints[-1]:
        raise ValueError("Breakpoints exceed song duration")

    song_file_bytes = await validated_song_file.read()
    cover_file_bytes = await validated_cover_file.read()

    song_extension = validated_song_file.filename.split(".")[-1]
    cover_extension = validated_cover_file.filename.split(".")[-1]

    # Create new song in database
    new_song = create_song_database(
        name=request.name,
        author=request.author,
        cover_src="",
        audio_src="",
        database_session=database_session
    )

    # Save media files
    song_location = create_song_files(new_song.song_id, song_extension, song_file_bytes, file_session)
    cover_location = create_cover_files(new_song.song_id, cover_extension, cover_file_bytes, file_session)

    # Update song record with media locations
    updated_song = update_song_database(
        song_id=new_song.song_id,
        cover_src=cover_location,
        audio_src=song_location,
        database_session=database_session
    )

    # Create slots from breakpoints
    create_slots_from_breakpoints_database(new_song.song_id, breakpoints, database_session=database_session)

    return updated_song


@router.delete("/{song_id}", response_model=DeleteResponse)
async def delete_song(
    song_id: int,
    database_session: Session = Depends(get_database_session),
    file_session: BaseFileSessionManager = Depends(get_file_session)
):
    # Remove media files
    remove_song_files(song_id, file_session)
    remove_cover_files(song_id, file_session)
    
    # Remove song entry from the database
    remove_song_database(song_id, database_session)

    return {"message": "Song and associated media deleted successfully"}


@router.get("/list", response_model=ListResponse)
async def list_songs(database_session: Session = Depends(get_database_session)):
    songs = list_all_songs_database(database_session=database_session)
    return {"songs": songs}


@router.get("/{song_id}", response_model=GetResponse)
async def get_song(song_id: int, database_session: Session = Depends(get_database_session)):
    song = get_song_database(song_id=song_id, database_session=database_session)
    return song
