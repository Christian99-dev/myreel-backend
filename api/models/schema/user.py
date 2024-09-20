from pydantic import BaseModel, EmailStr, Field


# POST /invite
class InviteRequest(BaseModel):
    groupid: str
    email: EmailStr


class InviteResponse(BaseModel):
    message: str

# POST /acceptInvite
class AcceptInviteRequest(BaseModel):
    invitationid: str
    token: str
    groupid: str
    name: str = Field(..., min_length=1, max_length=15)


class AcceptInviteResponse(BaseModel):
    jwt: str

# POST /loginRequest
class LoginRequestRequest(BaseModel):
    groupid: str
    email: str


class LoginRequestResponse(BaseModel):
    message: str
    pass

# POST /login
class LoginRequest(BaseModel):
    groupid: str
    pin: str
    email: str


class LoginResponse(BaseModel):
    jwt: str
    name: str
    user_id: int