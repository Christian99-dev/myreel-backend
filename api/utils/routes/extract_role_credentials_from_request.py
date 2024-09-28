import re
from typing import Optional

from fastapi import Request
from pydantic import BaseModel


class RoleCredentials(BaseModel):
    admintoken: Optional[str]
    jwt: Optional[str]
    groupid: Optional[str]
    editid: Optional[int]

async def extract_role_credentials_from_request(request: Request) -> RoleCredentials:
    # flags
    content_type = str(request.headers.get("content-type", ""))
    is_multipart_or_form = (
        content_type.startswith("multipart/form-data")
        or content_type.startswith("application/x-www-form-urlencoded"))

    # -- SUCHE NACH token oder jwt im HEADER -- #
    # Extrahiere die relevanten Informationen aus dem Header
    admintoken = request.headers.get('admintoken')
    jwt = request.headers.get('Authorization')  # Annahme: JWT wird im Authorization Header gesendet
    
    if jwt is not None and jwt.startswith("Bearer "):
        jwt = jwt.replace("Bearer ", "")

    # -- SUCHE NACH groupid oder editid im QUERY -- #
    groupid = request.query_params.get('groupid')
    editid = request.query_params.get('editid')
    
    # -- SUCHE NACH groupid oder editid im BODY NUR wenn es keine file ist -- #
    if not is_multipart_or_form:
        body = await request.json() if await request.body() else {}
        groupid = groupid or body.get('groupid')
        editid = editid or body.get('editid')    
    
    # -- SUCHE NACH groupid oder editid im PATH -- #
    path = request.url.path
    groupid_match = re.search(r'/group/([^/]+)', path)
    editid_match = re.search(r'/edit/(\d+)', path)

    if groupid_match:
        groupid = groupid_match.group(1)
    if editid_match:
        editid = int(editid_match.group(1))
        
    # Konvertiere editid in int, falls vorhanden und möglich
    try:
        editid = int(editid) if editid is not None else None
    except:
        editid = None

    

    return RoleCredentials(admintoken=admintoken, jwt=jwt, groupid=groupid, editid=editid)
