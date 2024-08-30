from pydantic import BaseModel

# POST /invite
class InviteRequest(BaseModel):
    groupid: str
    email: str


class InviteResponse(BaseModel):
    message: str

# POST /acceptInvite
class AcceptInviteRequest(BaseModel):
    invitationid: str
    token: str
    groupid: str
    name: str


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
    token: str


class LoginResponse(BaseModel):
    jwt: str