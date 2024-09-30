

from io import BytesIO
import logging

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from api.models.schema.slot import (AddSlotRequest, AddSlotResponse,
                                    ChangeSlotRequest, ChangeSlotResponse,
                                    DeleteSlotResponse, PreviewSlotRequest)
from api.services.database.occupied_slot import \
    create as create_occupied_slot_service
from api.services.database.occupied_slot import \
    get as get_occupied_slot_database
from api.services.database.occupied_slot import \
    is_slot_occupied as is_slot_occupied_database
from api.services.database.edit import update as update_edit_database
from api.services.database.occupied_slot import \
    remove as remove_occupied_slot_database
from api.services.database.occupied_slot import \
    update as update_occupied_slot_database
from api.services.files.demo_slot import get as get_demo_file
from api.services.database.slot import \
    get_slot_by_occupied_slot_id as get_slot_by_occupied_slot_id_database
from api.services.database.slot import get as get_slot_database
from api.services.files.edit import get as get_edit_file
from api.services.files.edit import update as update_edit_file
from api.services.files.occupied_slot import \
    create as create_occupied_slot_file
from api.services.files.occupied_slot import \
    remove as remove_occupied_slot_file
from api.services.files.occupied_slot import \
    update as update_occupied_slot_file
from api.sessions.database import get_database_session
from api.sessions.files import BaseFileSessionManager, get_file_session
from api.utils.files.file_validation import file_validation
from api.utils.jwt import jwt
from api.utils.media_manipulation.swap_slot_in_edit_video import \
    swap_slot_in_edit
from mock.database import data

logger = logging.getLogger("routes.slot")

# database

router = APIRouter(
    prefix="/edit",
)    

@router.delete("/{edit_id}/slot/{occupied_slot_id}", response_model=DeleteSlotResponse,  tags=["edit"])
async def delete_slot(
    edit_id: int,
    occupied_slot_id: int,
    authorization: str = Header(None), 
    database_session: Session = Depends(get_database_session), 
    file_session: BaseFileSessionManager = Depends(get_file_session)
):
    
    # optain information
    user_id = jwt.read_jwt(authorization.replace("Bearer ", ""))
    occupied_slot = get_occupied_slot_database(occupied_slot_id, database_session=database_session)
    slot = get_slot_by_occupied_slot_id_database(occupied_slot_id, database_session=database_session)
    

    # IMPORTANT, you can only delete your own slot
    if user_id != occupied_slot.user_id:
        raise HTTPException(status_code=403, detail="Slot not yours")
    
    # Eigentlich egal, da edit id nur für die authorisierung genutzt wird ob wir group member sind
    # Es würde bei jeder edit id funktionieren, die NUR in der gruppe ist
    if edit_id != occupied_slot.edit_id:
        raise HTTPException(status_code=403, detail=f"Edit has not occupied slot with id {edit_id}")
    
    # remove assets in db and files
    remove_occupied_slot_database(occupied_slot.occupied_slot_id, database_session)
    remove_occupied_slot_file(occupied_slot.occupied_slot_id, file_session)
    
    # demo file
    demo_video_bytes = get_demo_file(file_session)
    old_edit_file = get_edit_file(edit_id, file_session=file_session)

    # create new edit with demo slot
    new_edit_file = swap_slot_in_edit(
        old_edit_file,
        slot.start_time,
        slot.end_time,
        "mp4",
        
        demo_video_bytes,
        0,
        slot.end_time - slot.start_time,
        "mp4",
        
        "mp4"
    )
    
    # updateing file
    update_edit_file(edit_id, new_edit_file, file_session=file_session)
    
    return {"message": "Successfull delete"}

@router.post("/{edit_id}/slot/{slot_id}", response_model=AddSlotResponse,  tags=["edit"])
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
    if is_slot_occupied_database(slot_id, edit_id, database_session=database_session):
        raise HTTPException(status_code=403, detail="Slot ist schon belegt")
       
    slot = get_slot_database(slot_id, database_session=database_session)
    
    if slot.end_time - slot.start_time != request.end_time - request.start_time:
        raise HTTPException(status_code=422, detail="Slot länge muss die gleiche sein")
        
    # validate new video clip
    validated_video_file = file_validation(request.video_file, "video")
    validate_video_file_bytes = await validated_video_file.read()
    
    # database eintrag
    new_occupied_slot = create_occupied_slot_service(
        user_id,
        slot_id,
        edit_id,
        start_time=request.start_time,
        end_time=request.end_time,
        video_src="",
        database_session=database_session
    )
    
    # file eintrag in occupied slot
    video_location = create_occupied_slot_file(
        new_occupied_slot.occupied_slot_id, 
        "mp4", 
        validate_video_file_bytes, 
        file_session=file_session
    )
    
    # datenbank eintrag mit video src vervollständing
    update_occupied_slot_database(occupied_slot_id=new_occupied_slot.slot_id, database_session=database_session, video_src=video_location) 
    
    # edit neu erstellen und abspeicher
    old_edit_file = get_edit_file(edit_id, file_session=file_session)
    
    # schreibe den neuen clip in das vorhandene edit
    new_edit_file = swap_slot_in_edit(
        old_edit_file,
        slot.start_time,
        slot.end_time,
        "mp4",
        validate_video_file_bytes,
        new_occupied_slot.start_time,
        new_occupied_slot.end_time,
        "mp4",
        "mp4"
    )
    
    # speichere das neue edit ab
    update_edit_file(edit_id, new_edit_file, file_session=file_session)

    return {"message": "Successfull post"}

@router.put("/{edit_id}/slot/{occupied_slot_id}", response_model=ChangeSlotResponse,  tags=["edit"])
async def put_slot(
    edit_id: int,
    occupied_slot_id: int,
    authorization: str = Header(None), 
    request: ChangeSlotRequest = Depends(), 
    database_session: Session = Depends(get_database_session), 
    file_session: BaseFileSessionManager = Depends(get_file_session)
):
    # optain information
    user_id = jwt.read_jwt(authorization.replace("Bearer ", ""))
    occupied_slot = get_occupied_slot_database(occupied_slot_id, database_session=database_session)
    
    # IMPORTANT, you can only change your own slot
    if user_id != occupied_slot.user_id:
        raise HTTPException(status_code=403, detail="Slot not yours")
    
    # Eigentlich egal, da edit id nur für die authorisierung genutzt wird ob wir group member sind
    # Es würde bei jeder edit id funktionieren, die NUR in der gruppe ist
    if edit_id != occupied_slot.edit_id:
        raise HTTPException(status_code=403, detail=f"Edit has not occupied slot with id {edit_id}")
    
    # start und endzeit von slot
    slot = get_slot_by_occupied_slot_id_database(occupied_slot.occupied_slot_id, database_session=database_session)
    
    if slot.end_time - slot.start_time != request.end_time - request.start_time:
        raise HTTPException(status_code=422, detail="Slot länge muss die gleiche sein")
    
    # update occupied slot
    new_occupied_slot = update_occupied_slot_database(occupied_slot_id, start_time=request.start_time, end_time=request.end_time, database_session=database_session)
    
    # change video also ? 
    if request.video_file != None:
        # validate new video clip
        validated_video_file = file_validation(request.video_file, "video")
        validate_video_file_bytes = await validated_video_file.read()
                
        # edit neu erstellen und abspeicher
        old_edit_file = get_edit_file(edit_id, file_session=file_session)
        
        new_edit_file = swap_slot_in_edit(
            old_edit_file,
            slot.start_time,
            slot.end_time,
            "mp4",
            
            validate_video_file_bytes,
            new_occupied_slot.start_time,
            new_occupied_slot.end_time,
            "mp4",
            
            "mp4"
        )

        # neues edit abspeichern
        update_edit_file(edit_id, new_edit_file, file_session=file_session)

        # file updaten
        update_occupied_slot_file(occupied_slot.occupied_slot_id, validate_video_file_bytes, file_session=file_session)
    
    
    return {"message": "Successfull swap"}

@router.post("/{edit_id}/slot/{slot_id}/preview", tags=["edit"])
async def put_slot(
    edit_id: int,
    slot_id: int,
    request: PreviewSlotRequest = Depends(), 
    database_session: Session = Depends(get_database_session), 
    file_session: BaseFileSessionManager = Depends(get_file_session)
):
    # slot is free ? 
    try :
        if is_slot_occupied_database(slot_id, edit_id, database_session=database_session):
            raise HTTPException(status_code=403, detail="Slot ist schon belegt")
    except NoResultFound:
        pass
       
    slot = get_slot_database(slot_id, database_session=database_session)
    
    if slot.end_time - slot.start_time != request.end_time - request.start_time:
        raise HTTPException(status_code=422, detail="Slot länge muss die gleiche sein")
        
    # validate new video clip
    validated_video_file = file_validation(request.video_file, "video")
    validate_video_file_bytes = await validated_video_file.read()
    
    # edit neu erstellen und abspeicher
    old_edit_file = get_edit_file(edit_id, file_session=file_session)
    
    # schreibe den neuen clip in das vorhandene edit
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
    
    # Create a BytesIO object to hold the video bytes for streaming
    new_edit_bytes_io = BytesIO(new_edit_file)

    # Return the new edit file as a video stream with appropriate headers
    headers = {
        'Content-Disposition': 'attachment; filename="edited_video.mp4"'
    }

    return StreamingResponse(new_edit_bytes_io, media_type="video/mp4", headers=headers)

