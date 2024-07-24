from typing import Optional
from pydantic import BaseModel
from fastapi import Request

class RoleCredentials(BaseModel):
    admintoken: Optional[str]
    jwt: Optional[str]
    groupid: Optional[str]
    editid: Optional[int]

def extract_role_credentials_from_request(request: Request) -> RoleCredentials:
    # Extrahiere die relevanten Informationen aus dem Header
    admintoken = request.headers.get('admintoken')
    jwt = request.headers.get('Authorization')  # Annahme: JWT wird im Authorization Header gesendet
    
    if jwt is not None and jwt.startswith("Bearer "):
        jwt = jwt.replace("Bearer ", "")

    # Extrahiere die relevanten Informationen aus den Query-Parametern
    groupid = request.query_params.get('groupid')
    editid = request.query_params.get('editid')

    # Konvertiere editid in int, falls vorhanden
    editid = int(editid) if editid is not None else None

    return RoleCredentials(admintoken=admintoken, jwt=jwt, groupid=groupid, editid=editid)
