

import random
import string
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from api.config.media_access import media_access
from api.config.database import get_db
from api.config.media_access import BaseMediaAccess
from api.utils.media_manipulation.create_edit_video import create_edit_video
from api.utils.media_manipulation.swap_slot_in_edit_video import swap_slot_in_edit


router = APIRouter(
    prefix="/testing",
)    

@router.get("/1")
async def test1(db = Depends(get_db), media_access: BaseMediaAccess = Depends(lambda: media_access)):
    
    video_bytes = media_access.get("demo.mp4", "demo_slot")
    song_bytes = media_access.get("1.wav", "songs")
    
    breapoints = [1,2,3,4]
    
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
async def test2(db = Depends(get_db), media_access: BaseMediaAccess = Depends(lambda: media_access)):
    
    input_video_bytes = media_access.get("v5Jc.mp4", "testres")
    new_video_bytes   = media_access.get("1.mp4", "occupied_slots")
    
    endresult = swap_slot_in_edit(
        input_video_bytes,
        0,
        1,
        "mp4",
        new_video_bytes,
        2,
        3,
        "mp4",
        "mp4"
    )
    
    media_access.save("v5Jc_out.mp4", "testres", endresult)

    print("testing 2")
    return 17

@router.get("/3")
async def test3(db = Depends(get_db), media_access: BaseMediaAccess = Depends(lambda: media_access)):
    print("testing 3")
    return 17


def generate_random_characters():
    # Erstellen einer Liste von Zeichen (Buchstaben und Ziffern)
    characters = string.ascii_letters + string.digits
    # Wählen von 4 zufälligen Zeichen aus der Liste
    random_chars = ''.join(random.choice(characters) for _ in range(4))
    return random_chars

