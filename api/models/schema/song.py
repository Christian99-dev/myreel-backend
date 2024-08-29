from dataclasses import dataclass
from typing import List
from pydantic import BaseModel
from fastapi import Form, UploadFile, File    

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
    
