from typing import List
from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    id: int
    name: str
    role: str
    email: str

class Member(BaseModel):
    user_id: int
    role: str
    name: str

class Edit(BaseModel):
    edit_id: int
    created_by: Member
    name: str
    isLive: bool

# POST /
class PostRequest(BaseModel):
    groupname: str = Field(..., min_length=3, max_length=100, description="The name of the group.")
    username: str = Field(..., min_length=3, max_length=50, description="The name of the user.")
    email: EmailStr = Field(..., description="The email of the user.")

class PostResponse(BaseModel):
    jwt: str
    group_id: str


# DELETE /{group_id} 
class DeleteResponse(BaseModel):
    message: str

# GET /{group_id}/name
class GroupNameResponse(BaseModel):
    name: str

# GET /{group_id}
class GetResponse(BaseModel):
    user: User
    group_name: str
    group_id: str
    created_by: str

# GET /{group_id}
class GetMembersResponse(BaseModel):
    members: List[Member]

# GET /{group_id}
class GetEditsResponse(BaseModel):
    edits: List[Edit]