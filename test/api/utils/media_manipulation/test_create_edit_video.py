
from api.models.database.model import Song
from api.services.database.song import get_breakpoints
from api.services.files.demo_slot import get as get_demo_slot_mediaservice
from api.services.files.song import get as get_song_mediaservice
from api.utils.media_manipulation.create_edit_video import create_edit_video


def notest_create_edit_video_no_errors(memory_file_session, memory_database_session):
    
    # Arrange
    existing_song = memory_database_session.query(Song).first()  # Nimm den ersten Song
    assert existing_song is not None, "Kein vorhandener Song gefunden"

    song_id = existing_song.song_id
    
    demo_video_bytes = get_demo_slot_mediaservice(memory_file_session)
    song_bytes       = get_song_mediaservice(song_id, memory_file_session)
    
    breakpoints = get_breakpoints(song_id, memory_database_session)
    
    assert demo_video_bytes is not None
    assert song_bytes is not None
    
    # Act 
    result = create_edit_video(
        demo_video_bytes,
        "mp4",
        song_bytes,
        "mp3",
        breakpoints, 
        "mp4"
    )
    
    assert result is not None
    