
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse


router = APIRouter(
    prefix="/static",
)    

@router.get("/covers/{filename}")
async def serve_covers(filename: str):      
    file_path = f"static/covers/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@router.get("/demo_slot/{filename}")
async def serve_demo_slot(filename: str):   
    file_path = f"static/demo_slot/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@router.get("/edits/{filename}")
async def serve_edits(filename: str):
    file_path = f"static/edits/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@router.get("/occupied_slots/{filename}")
async def serve_occupied_slot(filename: str):
    file_path = f"static/occupied_slots/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@router.get("/songs/{filename}")
async def serve_songs(filename: str):
    file_path = f"static/songs/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)