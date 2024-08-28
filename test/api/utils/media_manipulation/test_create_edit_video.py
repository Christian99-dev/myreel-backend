
from api.models.database.model import Song
from api.services.media.demo_slot import get as get_demo_slot_mediaservice
from api.services.media.song import get as get_song_mediaservice
from api.services.database.song import get_breakpoints
from api.utils.media_manipulation.create_edit_video import create_edit_video


def notest_create_edit_video_no_errors(media_access_memory, db_memory):
    
    # Arrange
    existing_song = db_memory.query(Song).first()  # Nimm den ersten Song
    assert existing_song is not None, "Kein vorhandener Song gefunden"

    song_id = existing_song.song_id
    
    demo_video_bytes = get_demo_slot_mediaservice(media_access_memory)
    song_bytes       = get_song_mediaservice(song_id, media_access_memory)
    
    breakpoints = get_breakpoints(song_id, db_memory)
    
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
    