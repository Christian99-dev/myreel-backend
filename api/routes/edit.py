from typing import List
from wsgiref import validate
from fastapi import APIRouter, Body, Depends, HTTPException, Header, Request
from api.utils.jwt import jwt
from api.sessions.instagram import get_instagram_session
from api.sessions.files import BaseFileSessionManager
from api.models.schema.edit import AddSlotRequest, AddSlotResponse, ChangeSlotRequest, ChangeSlotResponse, DeleteEditResponse, DeleteSlotRequest, DeleteSlotResponse, EditListResponse,User, GetEditResponse, GoLiveResponse, PostRequest, Slot
from api.models.schema.edit import PostResponse
from api.services.database.edit import get as get_edit_serivce, remove
from api.services.database.occupied_slot import get_occupied_slots_for_edit, is_slot_occupied
from api.services.database.slot import get_slot_by_occupied_slot_id, get_slots_for_edit
from api.services.database.user import get as get_user_service
from api.services.files.demo_slot import get as get_demo_video
from api.services.files.song import get as get_song_audio
from api.services.files.edit import create as create_edit_media_access
from api.services.database.edit import are_all_slots_occupied, get_edits_by_group, set_is_live, update as edit_update_service
from api.services.database.song import  get_breakpoints
from api.services.database.occupied_slot import get as get_occupied_slot, remove as remove_occupied_slot_service
from api.services.instagram.upload import upload as instram_upload_service
from api.services.files.edit import get as get_edit_media_access, update as update_media_service
from api.services.database.edit import remove as remove_edit_service
from api.services.database.edit import create as create_edit_service
from api.services.files.edit import update as update_meida_edit_service
from api.services.files.occupied_slot import remove as remove_occupied_slot_media_service, create as create_occupied_slot_media_service, update as update_occupied_slot_media_service
from api.services.database.occupied_slot import create as create_occupied_slot_service
from api.services.database.occupied_slot import update as update_occupied_slot_service

# sessions
from api.sessions.database import get_database_session
from sqlalchemy.orm import Session
from api.utils.files.file_validation import file_validation
from api.utils.files.file_validation import file_validation
from api.utils.media_manipulation.create_edit_video import create_edit_video
from api.utils.media_manipulation.swap_slot_in_edit_video import swap_slot_in_edit
from api.sessions.files import get_file_session

# database

router = APIRouter(
    prefix="/edit",
)    

@router.post("/{edit_id}/goLive", response_model=GoLiveResponse, tags=["edit"])
def go_live(edit_id: int, database_session: Session = Depends(get_database_session), media_access: BaseFileSessionManager = Depends(get_file_session), instagram_access = Depends(get_instagram_session)):
    
    if not are_all_slots_occupied(edit_id, database_session=database_session):
        raise HTTPException(status_code=422, detail="Edit not upload ready, occupie all slots")
        
    # check if all slots are belegt 
    edit_file = get_edit_media_access(edit_id, media_access=media_access)
    
    if not edit_file:
        raise HTTPException(status_code=422, detail="Something went wrong, no videofile found")
    
    set_is_live(edit_id, database_session=database_session)
    
    if instram_upload_service(edit_file, "mp4", "was geht ab instagram", instagram_access):
        return {"message": "Auf instagram hochgeladen!"}
       
    
@router.delete("/{edit_id}", response_model=DeleteEditResponse, tags=["edit"])
async def delete_edit(edit_id: int, database_session: Session = Depends(get_database_session)):
    
    if remove_edit_service(edit_id, database_session=database_session):
        return {"message" : "Deleted Successfully"}
    else:
        raise HTTPException(status_code=422, detail="Could not delete")

@router.post("/", response_model=PostResponse, tags=["edit"])
def create_edit(
    request: PostRequest = Body(...),
    database_session: Session = Depends(get_database_session),
    media_access: BaseFileSessionManager = Depends(get_file_session),
    authorization: str = Header(None)
):        
    user_id = jwt.read_jwt(authorization.replace("Bearer ", ""))
    groupid = request.groupid
    
    if user_id is None or groupid is None:
        raise HTTPException(status_code=422, detail="Sorry, something went wrong")
    
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
    
    if new_edit is None: 
        raise HTTPException(status_code=422, detail="Problem when creating edit")
    
    # get demo video
    demo_video_bytes = get_demo_video(media_access)
    
    if demo_video_bytes is None: 
        raise HTTPException(status_code=422, detail="Problem with demo video")

    # get song
    song_audio_bytes = get_song_audio(request.song_id, media_access)
    
    if song_audio_bytes is None: 
        raise HTTPException(status_code=422, detail="Problem with song audio")
    
    # create edit video
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
    
    if edit_video_bytes is None:
        raise HTTPException(status_code=422, detail="Error creating edit")
        
    edit_location = create_edit_media_access(
        new_edit.edit_id, 
        "mp4", 
        edit_video_bytes, 
        media_access
    )
    
    if edit_location is None:
        raise HTTPException(status_code=422, detail="Something went wrong while saving the edit")
    
    # Update the edit with the new video source
    updated_edit = edit_update_service(new_edit.edit_id, video_src=edit_location, database_session=database_session)
    
    user = get_user_service(updated_edit.created_by, database_session)  # Retrieve the user details
    
    # Create the response object
    response = PostResponse(
        edit_id=updated_edit.edit_id,
        song_id=updated_edit.song_id,
        created_by=User(user_id=user.user_id, name=user.name),  # Assuming you have a way to get this, or replace with the user info if necessary
        group_id=updated_edit.group_id,
        name=updated_edit.name,
        isLive=updated_edit.isLive,
        video_src=updated_edit.video_src
    )

    return response
@router.get("/group/{group_id}/list", response_model=EditListResponse, tags=["edit"])
async def get_edits_for_group(group_id: str, database_session: Session = Depends(get_database_session)):
    # Abrufen aller Edits für die gegebene Gruppen-ID
    edits = get_edits_by_group(group_id, database_session)

    if not edits:
        raise HTTPException(status_code=404, detail="No edits found for this group")
    
    response_list = []
    
    for edit in edits:
        # Abrufen der User-Informationen des Erstellers
        user = get_user_service(edit.created_by, database_session)
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {edit.created_by} not found for edit")
        
        # Erstellung der EditWithUserObject-Instanz mit dem User-Objekt
        edit_info = {
            "edit_id": edit.edit_id,
            "song_id": edit.song_id,
            "created_by": User(user_id=user.user_id, name=user.name),  # User-Objekt mit ID und Name
            "group_id": edit.group_id,
            "name": edit.name,
            "isLive": edit.isLive,
            "video_src": edit.video_src
        }
        
        response_list.append(edit_info)
    
    return EditListResponse(edits=response_list)

@router.get("/group/{group_id}/{edit_id}", response_model=GetEditResponse,  tags=["edit"])
async def get_edit_details(group_id: str, edit_id: int, database_session: Session = Depends(get_database_session)):
    # Abrufen des Edits
    edit = get_edit_serivce(edit_id, database_session)

    if not edit or edit.group_id != group_id:
        raise HTTPException(status_code=404, detail="Edit not found in this group")

    # Abrufen der Slots und der belegten Slots über die Services
    slots = get_slots_for_edit(edit_id, database_session)
    occupied_slots_info = get_occupied_slots_for_edit(edit_id, database_session)

    # Umwandlung des edit-Objekts
    edit_response = {
        "edit_id": edit.edit_id,
        "song_id": edit.song_id,
        "created_by": {
            "user_id": edit.created_by,  # ID des Erstellers
            "name": edit.creator.name,    # Name des Erstellers
        },
        "group_id": edit.group_id,
        "name": edit.name,
        "isLive": edit.isLive,
        "video_src": edit.video_src
    }

    # Erstellung der Slot-Details für das Response-Modell
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
                occupied_id = occupied.occupied_slot_id  # Angenommen, occupied_slot_id existiert
                break
        
        slot_response.append({
            "slot_id": slot.slot_id,
            "song_id": slot.song_id,
            "start_time": slot.start_time,
            "end_time": slot.end_time,
            "occupied_by": occupied_info,  # Optionales User-Objekt
            "occupied_id": occupied_id  # ID des belegten Slots oder null
        })

    return {
        "edit": edit_response,
        "slots": slot_response  # Normale Slots (mit IDs und optionalem User)
    }


@router.delete("/group/{group_id}/{edit_id}/slot/{occupied_slot_id}", response_model=DeleteSlotResponse,  tags=["edit"])
async def delete_slot(
    occupied_slot_id: int,
    authorization: str = Header(None), 
    database_session: Session = Depends(get_database_session), 
    media_access: BaseFileSessionManager = Depends(get_file_session)
):
    
    user_id = jwt.read_jwt(authorization.replace("Bearer ", ""))
    occupied_slot = get_occupied_slot(occupied_slot_id, database_session=database_session)
    
    if occupied_slot is None:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    if user_id != occupied_slot.user_id:
        raise HTTPException(status_code=403, detail="Slot not yours")
    
    try:
        remove_occupied_slot_service(occupied_slot.occupied_slot_id, database_session)
        remove_occupied_slot_media_service(occupied_slot.occupied_slot_id, media_access)
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
    media_access: BaseFileSessionManager = Depends(get_file_session)
):
    
    user_id = jwt.read_jwt(authorization.replace("Bearer ", ""))
    
    # slot is free ? 
    if is_slot_occupied(slot_id, edit_id, database_session=database_session):
        raise HTTPException(status_code=403, detail="Slot is nicht leer")
 
    (validated_video_file, message) = file_validation(request.video_file, "video")
    
    if not validated_video_file:
        raise HTTPException(status_code=400, detail="File is not valid")
    
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
            media_access=media_access
        )
        
        # datenbank eintrag mit video src vervollständing
        updated_occupied_slot = update_occupied_slot_service(database_session=database_session,occupied_slot_id=new_occupied_slot.slot_id, video_src=video_location)
        
        # start und endzeit von slot
        slot = get_slot_by_occupied_slot_id(updated_occupied_slot.occupied_slot_id, database_session=database_session)        
        
        # edit neu erstellen und abspeicher
        old_edit_file = get_edit_media_access(edit_id, media_access=media_access)
        
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
        
        update_meida_edit_service(edit_id, "mp4", new_file, media_access=media_access)
        
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
    media_access: BaseFileSessionManager = Depends(get_file_session)
):
    user_id = jwt.read_jwt(authorization.replace("Bearer ", ""))

    # slot ist belegt und von mir ? 
    occupied_slot = get_occupied_slot(occupied_slot_id, database_session=database_session)
    
    if not occupied_slot:
        raise HTTPException(status_code=400, detail="Slot is empty")
    
    if occupied_slot.user_id is not user_id:
        raise HTTPException(status_code=403, detail="Slot is not yours")
    
    (validated_video_file, message) = file_validation(request.video_file, "video")
    validate_video_file_bytes = await validated_video_file.read()
    
    slot = get_slot_by_occupied_slot_id(occupied_slot.occupied_slot_id, database_session=database_session)        
    
    # new edit saved
    old_edit_file = get_edit_media_access(edit_id, media_access=media_access)
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
    update_meida_edit_service(edit_id, "mp4", new_edit_file, media_access=media_access)
    update_occupied_slot_media_service(occupied_slot.occupied_slot_id, "mp4", validate_video_file_bytes, media_access=media_access )
    
    return {"message": "Successfull swap"}

