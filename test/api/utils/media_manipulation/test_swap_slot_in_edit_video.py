from api.models.database.model import Edit
from api.services.files.demo_slot import get as get_demo_slot_mediaservice
from api.services.files.edit import get as get_edit_mediaservice
from api.utils.media_manipulation.swap_slot_in_edit_video import \
    swap_slot_in_edit


def notest_swap_slot_in_edit_video_no_errors(memory_file_session, memory_database_session):
    
    # Arrange
    existing_edit = memory_database_session.query(Edit).first()  # Nimm den ersten Song
    assert existing_edit is not None, "Kein vorhandenes Eidt gefunden"
    edit_id = existing_edit.edit_id

    demo_video_bytes = get_demo_slot_mediaservice(memory_file_session)
    assert demo_video_bytes is not None
    
    edit_video_bytes = get_edit_mediaservice(edit_id,memory_file_session)
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
    
