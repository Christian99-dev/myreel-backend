

import random
import string

from fastapi import APIRouter, Depends

from api.services.instagram.upload import upload
from api.sessions.database import get_database_session
from api.sessions.email import BaseEmailSessionManager, get_email_session
from api.sessions.files import BaseFileSessionManager, get_file_session
from api.sessions.instagram import (BaseInstagramSessionManager,
                                    get_instagram_session)
from api.utils.media_manipulation.create_edit_video import create_edit_video
from api.utils.media_manipulation.swap_slot_in_edit_video import \
    swap_slot_in_edit

router = APIRouter(
    prefix="/testing",
)    

@router.get("/1", tags=["testing"])
def test1(
    database_session = Depends(get_database_session), 
    file_session: BaseFileSessionManager = Depends(get_file_session)
):
    video_bytes = file_session.get("demo.mp4", "demo_slot")
    song_bytes = file_session.get("1.wav", "songs")
    
    breapoints = [1,2,3,6]
    
    endresult = create_edit_video(
        video_bytes,
        "mp4", 
        
        song_bytes, 
        "mp3",
        
        breapoints,   
        "mp4"
    )
    
    file_session.create(f"{generate_random_characters()}.mp4", "testres", endresult)
    return 18

@router.get("/2", tags=["testing"])
def test2(database_session = Depends(get_database_session), file_session: BaseFileSessionManager = Depends(get_file_session)):
    name = "9oB0"
    input_video_bytes = file_session.get(f"{name}.mp4", "testres")
    new_video_bytes   = file_session.get("1.mp4", "occupied_slots")
    
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
    
    file_session.create(f"{name}_out.mp4", "testres", endresult)
    return 17

@router.get("/3", tags=["testing"])
def test3(
        instagram_session: BaseInstagramSessionManager = Depends(get_instagram_session), 
        file_session: BaseFileSessionManager = Depends(get_file_session)
    ):
    name = "a85N"
    demo_video = file_session.get(f"{name}.mp4", "testres")
    upload(demo_video, "mp4", "was geht", instagram_session)
    return 17

@router.get("/4", tags=["testing"])
async def upload_file(
        email_session:      BaseEmailSessionManager         = Depends(get_email_session),
        database_session                                    = Depends(get_database_session),
        file_session:       BaseFileSessionManager          = Depends(get_file_session),
        instagram_session:  BaseInstagramSessionManager     = Depends(get_instagram_session)
    ):
    # invite("k.christian9@web.de", "testcode", "ttestid", "12111", email_session)
    return 17

    


def generate_random_characters():
    # Erstellen einer Liste von Zeichen (Buchstaben und Ziffern)
    characters = string.ascii_letters + string.digits
    # Wählen von 4 zufälligen Zeichen aus der Liste
    random_chars = ''.join(random.choice(characters) for _ in range(4))
    return random_chars