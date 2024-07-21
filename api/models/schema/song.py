from pydantic import BaseModel

class SongBase(BaseModel) : 
    name: str
    author: str
    cover_src: str
    audio_src: str
    
# /create
class CreateRequest(SongBase):
    pass
    
class CreateResponse(SongBase):
    song_id: int
    times_used: int


