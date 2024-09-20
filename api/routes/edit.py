

import logging

from fastapi import APIRouter, Body, Depends, Header, HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from api.models.schema.edit import (AddSlotRequest, AddSlotResponse,
                                    ChangeSlotRequest, ChangeSlotResponse,
                                    DeleteEditResponse, DeleteSlotResponse,
                                    GetEditResponse, GoLiveResponse,
                                    PostRequest, PostResponse, User)
from api.services.database.edit import are_all_slots_occupied
from api.services.database.edit import create as create_edit_service
from api.services.database.edit import get as get_edit_serivce
from api.services.database.edit import get_edits_by_group
from api.services.database.edit import remove
from api.services.database.edit import remove as remove_edit_service
from api.services.database.edit import set_is_live
from api.services.database.edit import update as edit_update_service
from api.services.database.occupied_slot import \
    create as create_occupied_slot_service
from api.services.database.occupied_slot import get as get_occupied_slot
from api.services.database.occupied_slot import (get_occupied_slots_for_edit,
                                                 is_slot_occupied)
from api.services.database.occupied_slot import \
    remove as remove_occupied_slot_service
from api.services.database.occupied_slot import \
    update as update_occupied_slot_service
from api.services.database.slot import (get_slot_by_occupied_slot_id,
                                        get_slots_for_edit)
from api.services.database.song import get_breakpoints
from api.services.database.user import get as get_user_service
from api.services.files.demo_slot import get as get_demo_video
from api.services.files.edit import create as create_edit_file_session
from api.services.files.edit import get as get_edit_file_session
from api.services.files.edit import update as update_meida_edit_service
from api.services.files.occupied_slot import \
    create as create_occupied_slot_media_service
from api.services.files.occupied_slot import \
    remove as remove_occupied_slot_media_service
from api.services.files.occupied_slot import \
    update as update_occupied_slot_media_service
from api.services.files.song import get as get_song_audio
from api.services.instagram.upload import upload as instram_upload_service
# sessions
from api.sessions.database import get_database_session
from api.sessions.files import BaseFileSessionManager, get_file_session
from api.sessions.instagram import get_instagram_session
from api.utils.files.file_validation import file_validation
from api.utils.jwt import jwt
from api.utils.media_manipulation.create_edit_video import create_edit_video
from api.utils.media_manipulation.swap_slot_in_edit_video import \
    swap_slot_in_edit

logger = logging.getLogger("routes.edit")

# database

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
    new_edit = create_edit_service(
        request.song_id, 
        user_id,
        groupid,
        request.edit_name,
        False,   
        video_src="",
        database_session=database_session
    )
    
    # get infos to create edit video
    demo_video_bytes = get_demo_video(file_session)
    song_audio_bytes = get_song_audio(request.song_id, file_session)
    breakpoints = get_breakpoints(request.song_id, database_session)

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
    edit_location = create_edit_file_session(
        new_edit.edit_id, 
        "mp4", 
        edit_video_bytes, 
        file_session
    )

    # Update the edit with the new video link
    updated_edit = edit_update_service(new_edit.edit_id, video_src=edit_location, database_session=database_session)
        
    return updated_edit
        
@router.get("/{edit_id}", response_model=GetEditResponse, tags=["edit"])
async def get_edit_details(edit_id: int, database_session: Session = Depends(get_database_session)):
    # Abrufen des Edits aus der Datenbank
    edit = get_edit_serivce(edit_id, database_session=database_session)
    
    # Abrufen der Slots und belegten Slots
    slots = get_slots_for_edit(edit_id, database_session)
    occupied_slots_info = get_occupied_slots_for_edit(edit_id, database_session)

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
    if not are_all_slots_occupied(edit_id, database_session=database_session):
        raise HTTPException(status_code=422, detail="Edit not upload ready, occupie all slots")
    
    # nehme edit video 
    edit_file = get_edit_file_session(edit_id, file_session=file_session)

    # lade es hoch
    instram_upload_service(edit_file, "mp4", "was geht ab instagram", instagram_session)
    
    # datenbank live setzen
    set_is_live(edit_id, database_session=database_session)
    
    return {"message": "Auf instagram hochgeladen!"}
       
@router.delete("/{edit_id}", response_model=DeleteEditResponse, tags=["edit"])
async def delete_edit(edit_id: int, database_session: Session = Depends(get_database_session)):
    remove_edit_service(edit_id, database_session=database_session)
    return {"message" : "Deleted Successfully"}





@router.delete("/group/{group_id}/{edit_id}/slot/{occupied_slot_id}", response_model=DeleteSlotResponse,  tags=["edit"])
async def delete_slot(
    occupied_slot_id: int,
    authorization: str = Header(None), 
    database_session: Session = Depends(get_database_session), 
    file_session: BaseFileSessionManager = Depends(get_file_session)
):
    
    user_id = jwt.read_jwt(authorization.replace("Bearer ", ""))
    occupied_slot = get_occupied_slot(occupied_slot_id, database_session=database_session)
    
    if occupied_slot is None:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    if user_id != occupied_slot.user_id:
        raise HTTPException(status_code=403, detail="Slot not yours")
    
    try:
        remove_occupied_slot_service(occupied_slot.occupied_slot_id, database_session)
        remove_occupied_slot_media_service(occupied_slot.occupied_slot_id, file_session)
    except Exception as e:
        raise HTTPException(status_code=500, detail={e})
    # check if im the slot "owner"
    
    return {"message": "Successfull delete"}

@router.post("/group/{group_id}/{edit_id}/slot/{slot_id}", response_model=AddSlotResponse,  tags=["edit"])
async def post_slot(
    slot_id: int,
    edit_id: int,
    authorization: str = Header(None), 
    request: AddSlotRequest = Depends(), 
    database_session: Session = Depends(get_database_session), 
    file_session: BaseFileSessionManager = Depends(get_file_session)
):
    
    user_id = jwt.read_jwt(authorization.replace("Bearer ", ""))
    
    # slot is free ? 
    if is_slot_occupied(slot_id, edit_id, database_session=database_session):
        raise HTTPException(status_code=403, detail="Slot is nicht leer")
 
    validated_video_file = file_validation(request.video_file, "video")
    
    validate_video_file_bytes = await validated_video_file.read()
    
    try:     
        
        # database eintrag
        new_occupied_slot = create_occupied_slot_service(
            user_id,
            slot_id,
            edit_id,
            video_src="",
            database_session=database_session
        )
        
        # file eintrag in occupied slot
        video_location = create_occupied_slot_media_service(
            new_occupied_slot.occupied_slot_id, 
            "mp4", 
            validated_video_file, 
            file_session=file_session
        )
        
        # datenbank eintrag mit video src vervollständing
        updated_occupied_slot = update_occupied_slot_service(database_session=database_session,occupied_slot_id=new_occupied_slot.slot_id, video_src=video_location)
        
        # start und endzeit von slot
        slot = get_slot_by_occupied_slot_id(updated_occupied_slot.occupied_slot_id, database_session=database_session)        
        
        # edit neu erstellen und abspeicher
        old_edit_file = get_edit_file_session(edit_id, file_session=file_session)
        
        new_file = swap_slot_in_edit(
            old_edit_file,
            slot.start_time,
            slot.end_time,
            "mp4",
            validate_video_file_bytes,
            request.start_time,
            request.end_time,
            "mp4",
            "mp4"
        )
        
        update_meida_edit_service(edit_id, "mp4", new_file, file_session=file_session)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail={e})
    
    # wenn ja dann video rein
    return {"message": "Successfull post"}


@router.put("/group/{group_id}/{edit_id}/slot/{occupied_slot_id}", response_model=ChangeSlotResponse,  tags=["edit"])
async def put_slot(
    edit_id: int,
    occupied_slot_id: int,
    authorization: str = Header(None), 
    request: ChangeSlotRequest = Depends(), 
    database_session: Session = Depends(get_database_session), 
    file_session: BaseFileSessionManager = Depends(get_file_session)
):
    user_id = jwt.read_jwt(authorization.replace("Bearer ", ""))

    # slot ist belegt und von mir ? 
    occupied_slot = get_occupied_slot(occupied_slot_id, database_session=database_session)
    
    if not occupied_slot:
        raise HTTPException(status_code=400, detail="Slot is empty")
    
    if occupied_slot.user_id is not user_id:
        raise HTTPException(status_code=403, detail="Slot is not yours")
    
    validated_video_file = file_validation(request.video_file, "video")
    validate_video_file_bytes = await validated_video_file.read()
    
    slot = get_slot_by_occupied_slot_id(occupied_slot.occupied_slot_id, database_session=database_session)        
    
    # new edit saved
    old_edit_file = get_edit_file_session(edit_id, file_session=file_session)
    new_edit_file = swap_slot_in_edit(
        old_edit_file,
        slot.start_time,
        slot.end_time,
        "mp4",
        
        validate_video_file_bytes,
        request.start_time,
        request.end_time,
        "mp4",
        
        "mp4"
    )
    update_meida_edit_service(edit_id, "mp4", new_edit_file, file_session=file_session)
    update_occupied_slot_media_service(occupied_slot.occupied_slot_id, "mp4", validate_video_file_bytes, file_session=file_session )
    
    return {"message": "Successfull swap"}

