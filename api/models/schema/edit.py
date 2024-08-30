from dataclasses import dataclass
from typing import List, Optional
from fastapi import File, Form, UploadFile
from pydantic import BaseModel
from sqlalchemy import Float

#
class Edit(BaseModel):
    edit_id:int
    song_id:int
    created_by:int
    group_id:str
    name:str
    isLive:bool
    video_src:str
    
class EditWithCreatorName(BaseModel):
    edit_id:int
    song_id:int
    created_by: str
    group_id:str
    name:str
    isLive:bool
    video_src:str
    
class User(BaseModel):
    user_id: int
    name: str

class Slot(BaseModel):
    slot_id: int
    song_id: int
    start_time: float
    end_time: float
    occupied_by: Optional[User]  # Optionales User-Objekt


# POST /{editid}/goLive/
class GoLiveResponse(BaseModel):
    message: str 

# DELETE /{edit_id} 
class DeleteEditResponse(BaseModel):
    message: str 

# POST / 
class PostRequest(BaseModel):
    groupid: str
    song_id: int
    edit_name: str

class PostResponse(Edit):
    pass

# GET /group/{groupid}/list
class EditListResponse(BaseModel):
    edits: List[EditWithCreatorName]
    
# GET /group/{group_id}/{edit_id}
class GetEditResponse(BaseModel):
    edit_id: int
    song_id: int
    created_by: User
    group_id: str
    name: str
    isLive: bool
    video_src: str
    slots: List[Slot] 
    
# POST /group/{group_id}/{edit_id}/slot/{slot_id}
@dataclass
class AddSlotRequest():
    start_time:     float = Form(...)
    end_time:       float = Form(...)
    video_file: UploadFile = File(...)   

class AddSlotResponse(BaseModel):
    message: str

# DELETE /group/{group_id}/{edit_id}/slot/{slot_id}
@dataclass
class DeleteSlotRequest:
    video_file: UploadFile = File(...)   

class DeleteSlotResponse(BaseModel):
    message: str

# PUT /group/{group_id}/{edit_id}/slot/{slot_id}
@dataclass
class ChangeSlotRequest:
    start_time:     float = Form(...)
    end_time:       float = Form(...)
    video_file: UploadFile = File(...)      

class ChangeSlotResponse(BaseModel):
    message: str