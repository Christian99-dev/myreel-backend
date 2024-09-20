

import logging

from fastapi import APIRouter, Body, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from api.models.schema.edit import (DeleteEditResponse, GetEditResponse,
                                    GoLiveResponse, PostRequest, PostResponse)
from api.services.database.edit import \
    are_all_slots_occupied as are_all_slots_occupied_edit_database
from api.services.database.edit import create as create_edit_database
from api.services.database.edit import get as get_edit_database
from api.services.database.edit import remove as remove_edit_database
from api.services.database.edit import set_is_live as set_is_live_edit_database
from api.services.database.edit import update as edit_update_database
from api.services.database.occupied_slot import \
    get_occupied_slots_for_edit as get_occupied_slots_for_edit_database
from api.services.database.slot import \
    get_slots_for_edit as get_slots_for_edit_database
from api.services.database.song import \
    get_breakpoints as get_breakpoints_database
from api.services.files.demo_slot import get as get_demo_file
from api.services.files.edit import create as create_edit_file
from api.services.files.edit import get as get_edit_file
from api.services.files.song import get as get_song_file
from api.services.instagram.upload import upload as upload_instagram
from api.sessions.database import get_database_session
from api.sessions.files import BaseFileSessionManager, get_file_session
from api.sessions.instagram import get_instagram_session
from api.utils.jwt import jwt
from api.utils.media_manipulation.create_edit_video import create_edit_video

logger = logging.getLogger("routes.edit")

router = APIRouter(
    prefix="/edit",
)    

@router.post("/", response_model=PostResponse, tags=["edit"])
def create_edit(
    request: PostRequest = Body(...),
    database_session: Session = Depends(get_database_session),
    file_session: BaseFileSessionManager = Depends(get_file_session),
    authorization: str = Header(None)
):        
    user_id = jwt.read_jwt(authorization.replace("Bearer ", ""))
    groupid = request.groupid
    
    # create db edit
    new_edit = create_edit_database(
        request.song_id, 
        user_id,
        groupid,
        request.edit_name,
        False,   
        video_src="",
        database_session=database_session
    )
    
    # get infos to create edit video
    demo_video_bytes = get_demo_file(file_session)
    song_audio_bytes = get_song_file(request.song_id, file_session)
    breakpoints = get_breakpoints_database(request.song_id, database_session)

    # creating video
    edit_video_bytes = create_edit_video(
        demo_video_bytes,
        "mp4",
        song_audio_bytes,
        "mp3",
        breakpoints,
        "mp4"
    )

    # save video, obtain link
    edit_location = create_edit_file(
        new_edit.edit_id, 
        "mp4", 
        edit_video_bytes, 
        file_session
    )

    # Update the edit with the new video link
    updated_edit = edit_update_database(new_edit.edit_id, video_src=edit_location, database_session=database_session)
        
    return updated_edit
        
@router.get("/{edit_id}", response_model=GetEditResponse, tags=["edit"])
async def get_edit_details(edit_id: int, database_session: Session = Depends(get_database_session)):
    # Abrufen des Edits aus der Datenbank
    edit = get_edit_database(edit_id, database_session=database_session)
    
    # Abrufen der Slots und belegten Slots
    slots = get_slots_for_edit_database(edit_id, database_session)
    occupied_slots_info = get_occupied_slots_for_edit_database(edit_id, database_session)

    # Erstellerinformationen
    created_by = {
        "user_id": edit.creator.user_id,  # User-ID des Erstellers
        "name": edit.creator.name  # Name des Erstellers
    }

    # Edit-Informationen
    edit_info = {
        "edit_id": edit.edit_id,
        "song_id": edit.song_id,
        "group_id": edit.group_id,
        "created_by": edit.created_by,  # User-ID des Erstellers
        "name": edit.name,
        "isLive": edit.isLive,
        "video_src": edit.video_src
    }

    # Slot-Informationen
    slot_response = []
    for slot in slots:
        occupied_info = None
        occupied_id = None

        # Überprüfen, ob der Slot belegt ist
        for occupied in occupied_slots_info:

            if occupied.slot_id == slot.slot_id:
                occupied_info = {
                    "user_id": occupied.user.user_id,
                    "name": occupied.user.name
                }
                occupied_id = occupied.occupied_slot_id
                break

        slot_response.append({
            "slot_id": slot.slot_id,
            "song_id": slot.song_id,
            "start_time": slot.start_time,
            "end_time": slot.end_time,
            "occupied_by": occupied_info,
            "occupied_id": occupied_id
        })

    # Rückgabe im Format von GetEditResponse
    return {
        "created_by": created_by,
        "edit": edit_info,
        "slots": slot_response
    }

@router.post("/{edit_id}/goLive", response_model=GoLiveResponse, tags=["edit"])
def go_live(edit_id: int, database_session: Session = Depends(get_database_session), file_session: BaseFileSessionManager = Depends(get_file_session), instagram_session = Depends(get_instagram_session)):
    
    # check if all slots are belegt 
    if not are_all_slots_occupied_edit_database(edit_id, database_session=database_session):
        raise HTTPException(status_code=422, detail="Edit not upload ready, occupie all slots")
    
    # nehme edit video 
    edit_file = get_edit_file(edit_id, file_session=file_session)

    # lade es hoch
    upload_instagram(edit_file, "mp4", "was geht ab instagram", instagram_session)
    
    # datenbank live setzen
    set_is_live_edit_database(edit_id, database_session=database_session)
    
    return {"message": "Auf instagram hochgeladen!"}
       
@router.delete("/{edit_id}", response_model=DeleteEditResponse, tags=["edit"])
async def delete_edit(edit_id: int, database_session: Session = Depends(get_database_session)):
    remove_edit_database(edit_id, database_session=database_session)
    return {"message" : "Deleted Successfully"}
