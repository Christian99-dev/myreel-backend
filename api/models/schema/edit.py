
from typing import List, Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    user_id: int
    name: str

class Slot(BaseModel):
    slot_id: int
    song_id: int
    start_time: float
    end_time: float
    occupied_by: Optional[User]  
    occupied_id: Optional[int]
    video_src: Optional[str]
    
class Edit(BaseModel):
    edit_id: int
    song_id: int
    group_id: str
    created_by: int
    name: str
    isLive: bool
    video_src: str

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
    edit_name: str = Field(..., min_length=3, max_length=20)

class PostResponse(Edit):
    pass

# GET /{edit_id}
class GetEditResponse(BaseModel):
    created_by: User
    edit: Edit
    slots: List[Slot]