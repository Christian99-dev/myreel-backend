

import random
import string
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from api.config.email_access import email_access, BaseEmailAccess
from api.config.instagram_access import instagram_access, BaseInstagramAccess
from api.config.media_access import media_access
from api.config.database import get_db
from api.config.media_access import BaseMediaAccess
from api.services.email.invite import invite
from api.services.email.login import login
from api.services.instagram.upload import upload
from api.utils.files.file_validation import file_validation
from api.utils.media_manipulation.create_edit_video import create_edit_video
from api.utils.media_manipulation.swap_slot_in_edit_video import swap_slot_in_edit
from fastapi import FastAPI, File, UploadFile, HTTPException


router = APIRouter(
    prefix="/testing",
)    

@router.get("/1")
def test1(db = Depends(get_db), media_access: BaseMediaAccess = Depends(lambda: media_access)):
    
    video_bytes = media_access.get("demo.mp4", "demo_slot")
    song_bytes = media_access.get("1.wav", "songs")
    
    breapoints = [1,2,3,6]
    
    endresult = create_edit_video(
        video_bytes,
        "mp4", 
        
        song_bytes, 
        "mp3",
        
        breapoints,   
        "mp4"
    )
    
    media_access.save(f"{generate_random_characters()}.mp4", "testres", endresult)
    return 18

@router.get("/2")
def test2(db = Depends(get_db), media_access: BaseEmailAccess = Depends(lambda: media_access)):
    name = "sPN5"
    input_video_bytes = media_access.get(f"{name}.mp4", "testres")
    new_video_bytes   = media_access.get("1.mp4", "occupied_slots")
    
    endresult = swap_slot_in_edit(
        input_video_bytes,
        0,
        1,
        "mp4",
        new_video_bytes,
        0,
        1,
        "mp4",
        "mp4"
    )
    
    media_access.save(f"{name}_out.mp4", "testres", endresult)

    print("testing 2")
    return 17

@router.get("/3")
def test3(instagram_access: BaseInstagramAccess = Depends(lambda: instagram_access), media_access: BaseEmailAccess = Depends(lambda: media_access)):
    name = "jp67"
    demo_video = media_access.get(f"{name}.mp4", "testres")
    upload(demo_video, "mp4", "was geht", instagram_access)
    return 17

@router.post("/4")
async def upload_file(file: UploadFile = File(...)):
    file_type = "video"
    """Endpunkt zum Hochladen einer Datei und Validierung basierend auf dem Dateityp."""
    (validated_file, message) = file_validation(file, file_type)
    
    # Überprüfe, ob die Datei gültig ist
    if validated_file is None:
        raise HTTPException(status_code=400, detail=message)

    # Hier kannst du die Datei speichern oder weiterverarbeiten
    # Beispielsweise:
    # with open(f"./uploads/{validated_file.filename}", "wb") as f:
    #     f.write(await validated_file.read())

    return {"filename": validated_file.filename, "file_type": file_type}


def generate_random_characters():
    # Erstellen einer Liste von Zeichen (Buchstaben und Ziffern)
    characters = string.ascii_letters + string.digits
    # Wählen von 4 zufälligen Zeichen aus der Liste
    random_chars = ''.join(random.choice(characters) for _ in range(4))
    return random_chars