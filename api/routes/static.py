
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse


router = APIRouter(
    prefix="/files",
)    

@router.get("/covers/{filename}", tags=["files"])
async def serve_covers(filename: str):      
    file_path = f"outgoing/files/covers/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@router.get("/demo_slot/{filename}", tags=["files"])
async def serve_demo_slot(filename: str):   
    file_path = f"outgoing/files/demo_slot/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@router.get("/edits/{filename}", tags=["files"])
async def serve_edits(filename: str):
    file_path = f"outgoing/files/edits/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@router.get("/occupied_slots/{filename}", tags=["files"])
async def serve_occupied_slot(filename: str):
    file_path = f"outgoing/files/occupied_slots/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@router.get("/songs/{filename}", tags=["files"])
async def serve_songs(filename: str):
    file_path = f"outgoing/files/songs/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)