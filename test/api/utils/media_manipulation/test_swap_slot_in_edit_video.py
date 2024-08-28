from api.models.database.model import Edit
from api.services.media.demo_slot import get as get_demo_slot_mediaservice
from api.services.media.edit import get as get_edit_mediaservice
from api.utils.media_manipulation import swap_slot_in_edit_video
from api.utils.media_manipulation.swap_slot_in_edit_video import swap_slot_in_edit
from api.services.media.demo_slot import get as get_demo_slot_mediaservice

def notest_swap_slot_in_edit_video_no_errors(media_access_memory, db_memory):
    
    # Arrange
    existing_edit = db_memory.query(Edit).first()  # Nimm den ersten Song
    assert existing_edit is not None, "Kein vorhandenes Eidt gefunden"
    edit_id = existing_edit.edit_id

    demo_video_bytes = get_demo_slot_mediaservice(media_access_memory)
    assert demo_video_bytes is not None
    
    edit_video_bytes = get_edit_mediaservice(edit_id,media_access_memory)
    assert edit_video_bytes is not None
    
    result = swap_slot_in_edit(
        edit_video_bytes,
        1,
        2,
        "mp4",
        
        demo_video_bytes,
        1,
        2,
        "mp4",
        
        "mp4"
    )
    
    assert result is not None
    
