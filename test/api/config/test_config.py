from api.models.database.model import Song 
from sqlalchemy.orm import Session

def test_session_isolation(db_session: Session):
    """Test to ensure that each test function gets a separate session."""
    
    # Add a song to the database in this session
    song = Song(name="Test Song", author="Test Author", times_used=0, cover_src="http://example.com/cover.jpg", audio_src="http://example.com/audio.mp3")
    db_session.add(song)
    db_session.commit()
    
    # Check if the song is in the database
    result = db_session.query(Song).filter_by(name="Test Song").first()
    assert result is not None, "The song should be present in the database in this session."

def test_session_isolation_other(db_session: Session):
    """Test to ensure that changes in one session do not affect another session."""
    
    # Check that the previous test did not affect this session
    result = db_session.query(Song).filter_by(name="Test Song").first()
    assert result is None, "The song should not be present in this session if isolation is correct."