from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, Header, Request
from api.auth import jwt
from api.config.instagram_access import get_instagram_access
from api.config.media_access import BaseMediaAccess, get_media_access
from api.models.schema.edit import DeleteEditResponse, EditListResponse,User, GetEditResponse, GoLiveResponse, PostRequest, Slot
from api.models.schema.edit import PostResponse
from api.services.database.edit import get as get_edit_serivce
from api.services.database.occupied_slot import get_occupied_slots_for_edit
from api.services.database.slot import get_slots_for_edit
from api.services.database.user import get as get_user_service
from api.services.media.demo_slot import get as get_demo_video
from api.services.media.song import get as get_song_audio
from api.services.media.edit import create as create_edit_media_access
from api.services.database.edit import are_all_slots_occupied, get_edits_by_group, set_is_live, update as edit_update_service
from api.services.database.song import  get_breakpoints
from api.services.instagram.upload import upload as instram_upload_service
from api.services.media.edit import get as get_edit_media_access
from api.services.database.edit import remove as remove_edit_service
from api.services.database.edit import create as create_edit_service

# sessions
from api.config.database import Session, get_db
from api.utils.media_manipulation.create_edit_video import create_edit_video

# database

router = APIRouter(
    prefix="/edit",
)    

@router.post("/{edit_id}/goLive", response_model=GoLiveResponse, tags=["edit"])
def go_live(edit_id: int, db: Session = Depends(get_db), media_access: BaseMediaAccess = Depends(get_media_access), instagram_access = Depends(get_instagram_access)):
    
    if not are_all_slots_occupied(edit_id, db=db):
        raise HTTPException(status_code=422, detail="Edit not upload ready, occupie all slots")
        
    # check if all slots are belegt 
    edit_file = get_edit_media_access(edit_id, media_access=media_access)
    
    if not edit_file:
        raise HTTPException(status_code=422, detail="Something went wrong, no videofile found")
    
    set_is_live(edit_id, db=db)
    
    if instram_upload_service(edit_file, "mp4", "was geht ab instagram", instagram_access):
        return {"message": "Auf instagram hochgeladen!"}
       
    
@router.delete("/{edit_id}", response_model=DeleteEditResponse, tags=["edit"])
async def delete_edit(edit_id: int, db: Session = Depends(get_db)):
    
    if remove_edit_service(edit_id, db=db):
        return {"message" : "Deleted Successfully"}
    else:
        raise HTTPException(status_code=422, detail="Could not delete")

@router.post("/", response_model=PostResponse, tags=["edit"])
def create_edit(
    request: PostRequest = Body(...),
    db: Session = Depends(get_db),
    media_access: BaseMediaAccess = Depends(get_media_access),
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
        db=db
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
    breakpoints = get_breakpoints(request.song_id, db)
    
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
    
    
    updated_edit = edit_update_service(new_edit.edit_id, video_src=edit_location, db=db)
    
    return updated_edit

@router.get("/group/{group_id}/list", response_model=EditListResponse, tags=["edit"])
async def get_edits_for_group(group_id: str, db: Session = Depends(get_db)):
    # Abrufen aller Edits für die gegebene Gruppen-ID
    edits = get_edits_by_group(group_id, db)

    if not edits:
        raise HTTPException(status_code=404, detail="No edits found for this group")
    
    response_list = []
    
    for edit in edits:
        # Abrufen der User-Informationen des Erstellers
        user = get_user_service(edit.created_by, db)
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {edit.created_by} not found for edit")
        
        # Erstellung der EditListResponse-Instanz mit dem User-Namen
        edit_info = {
            "edit_id":edit.edit_id,
            "song_id":edit.song_id,
            "created_by":user.name,  
            "group_id":edit.group_id,
            "name":edit.name,
            "isLive":edit.isLive,
            "video_src":edit.video_src
        }
        
        response_list.append(edit_info)
    
    return {"edits":response_list}

@router.get("/group/{group_id}/{edit_id}", response_model=GetEditResponse,  tags=["edit"])
async def get_edit_details(group_id: str, edit_id: int, db: Session = Depends(get_db)):
        # Abrufen des Edits
    edit = get_edit_serivce(edit_id, db)

    if not edit or edit.group_id != group_id:
        raise HTTPException(status_code=404, detail="Edit not found in this group")

    # Abrufen der Slots und der belegten Slots über die Services
    slots = get_slots_for_edit(edit_id, db)
    occupied_slots_info = get_occupied_slots_for_edit(edit_id, db)

    # Erstellung der SlotDetail-Liste
    slot_details = []
    for slot in slots:
        occupied_user = None
        for occupied in occupied_slots_info:
            if occupied.slot_id == slot.slot_id:
                occupied_user = User(user_id=occupied.user.user_id, name=occupied.user.name)
                break

        slot_details.append(Slot(
            slot_id=slot.slot_id,
            song_id=slot.song_id,
            start_time=slot.start_time,
            end_time=slot.end_time,
            occupied_by=occupied_user
        ))

    response = GetEditResponse(
        edit_id=edit.edit_id,
        song_id=edit.song_id,
        created_by=User(user_id=edit.created_by, name=edit.creator.name),
        group_id=edit.group_id,
        name=edit.name,
        isLive=edit.isLive,
        video_src=edit.video_src,
        slots=slot_details
    )

    return response