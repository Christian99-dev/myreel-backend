from typing import List
from pydantic import BaseModel

class SongBase(BaseModel): 
    name: str
    author: str
    cover_src: str
    audio_src: str
    
class Song(SongBase):
    times_used: int
    song_id: int
    
# /create
class CreateRequest(SongBase):
    pass
    
class CreateResponse(Song):
    pass
    
# /list
class ListResponse(BaseModel):
    songs: List[Song]
    
# /get
class GetResponse(Song):
    pass

