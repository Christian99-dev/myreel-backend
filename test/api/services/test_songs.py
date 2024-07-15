import pytest
from sqlalchemy.orm import Session
from api.services.songs import create
from api.models.database.models import Song

def test_create_song(db_session: Session):
    # Arrange: Set up the parameters for the new song
    name = "Test Song"
    author = "Test Author"
    cover_src = "http://example.com/cover.jpg"
    audio_src = "http://example.com/audio.mp3"

    # Act: Call the create service function
    new_song = create(name, author, cover_src, audio_src, db_session)
    
    # Assert: Check the created song's attributes
    assert new_song.name == name
    assert new_song.author == author
    assert new_song.cover_src == cover_src
    assert new_song.audio_src == audio_src
    assert new_song.times_used == 0

    # Verify: Ensure the song was actually added to the database
    song_in_db = db_session.query(Song).filter_by(song_id=new_song.song_id).one_or_none()
    assert song_in_db is not None
    assert song_in_db.name == name
    assert song_in_db.author == author
    assert song_in_db.cover_src == cover_src
    assert song_in_db.audio_src == audio_src
