from dataclasses import dataclass
from typing import List

from fastapi import File, Form, UploadFile
from pydantic import BaseModel


class Song(BaseModel):
    name: str
    author: str
    times_used: int
    song_id: int
    cover_src: str
    audio_src: str
    
# / POST
@dataclass
class PostRequest():
    name: str                   = Form(...) 
    author: str                 = Form(...)  
    breakpoints: list[float]    = Form(...)  
    song_file: UploadFile       = File(...)  
    cover_file: UploadFile      = File(...)   

class PostResponse(Song):
    pass

# / LIST
class ListResponse(BaseModel):
    songs: List[Song]
   
# / DELETE 
class DeleteResponse(BaseModel):
    message: str

# / REMOVE 
class GetResponse(Song):
    pass
    
