from pydantic import BaseModel

class User(BaseModel):
    user_id: int
    group_id: str
    role: str
    name: str
    email: str

class Group(BaseModel):
    group_id: str
    name: str

# POST /{group_id} 
class PostRequest(BaseModel):
    groupname: str
    username: str
    email: str

class PostResponse(Group):
    jwt: str

# DELETE /{group_id} 
class DeleteResponse(BaseModel):
    message: str

# GET /{group_id} 
class GetResponse(Group):
    pass

# GET /{group_id}/groupExists
class GroupExistsResponse(BaseModel):
    exists: bool
