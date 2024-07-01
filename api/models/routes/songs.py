from pydantic import BaseModel


# abstractions
class Song(BaseModel):
    song_id: int
    name: str
    author: str
    times_used: int
    cover_src: str
    audio_src: str

    class Config:
        from_attributes = True

# /create
class CreateRequest(BaseModel):
    name: str
    author: str
    cover_src: str
    audio_src: str

class CreateResponse(BaseModel):
    message: str
    song: Song


