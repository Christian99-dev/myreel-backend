from dataclasses import dataclass

from fastapi import File, Form, UploadFile
from pydantic import BaseModel


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
    video_file: UploadFile = File(None)      

class ChangeSlotResponse(BaseModel):
    message: str
    
# PUT /group/{group_id}/{edit_id}/slot/{slot_id}/preview
@dataclass
class PreviewSlotRequest:
    start_time:     float = Form(...)
    end_time:       float = Form(...)
    video_file: UploadFile = File(...)      