from pydantic import BaseModel

# /create
class CreateRequest(BaseModel):
    name: str
    author: str
    cover_src: str
    audio_src: str

class CreateResponse(BaseModel):
    message: str


