
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from api.config import media_access
from api.config.database import get_db
from api.config.media_access import BaseMediaAccess


router = APIRouter(
    prefix="/testing",
)    

@router.get("/1")
async def test1(db = Depends(get_db), media_access: BaseMediaAccess = Depends(lambda: media_access)):
    print("testing 1")
    
    return 17

@router.get("/2")
async def test2(db = Depends(get_db), media_access: BaseMediaAccess = Depends(lambda: media_access)):
    print("testing 2")
    return 17

@router.get("/3")
async def test3(db = Depends(get_db), media_access: BaseMediaAccess = Depends(lambda: media_access)):
    print("testing 3")
    return 17

