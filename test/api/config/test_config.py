from sqlalchemy.orm import Session
from api.models.database.model import Song  # Adjust import path as per your project structure

def test_session_isolation(db_session: Session):
    """Test to ensure that each test function gets a separate session."""
    
    # Check if the database is empty at the beginning of the test
    assert db_session.query(Song).count() == 0, "Database should be empty at the beginning of this test."

    # Add a song to the database in this session
    song = Song(name="Test Song", author="Test Author", times_used=0, cover_src="http://example.com/cover.jpg", audio_src="http://example.com/audio.mp3")
    db_session.add(song)
    db_session.commit()
    
    # Check if the song is in the database
    result = db_session.query(Song).filter_by(name="Test Song").first()
    assert result is not None, "The song should be present in the database in this session."

def test_session_isolation_other(db_session: Session):
    """Test to ensure that changes in one session do not affect another session."""
    
    # Check if the database is empty at the beginning of the test
    assert db_session.query(Song).count() == 0, "Database should be empty at the beginning of this test."

    # Check that the previous test did not affect this session
    result = db_session.query(Song).filter_by(name="Test Song").first()
    assert result is None, "The song should not be present in this session if isolation is correct."
    
    
def test_session_isolation_filled(db_session_filled: Session):
    """Test to ensure that each test function gets a separate session."""
    
    # Check if the database is empty at the beginning of the test
    assert db_session_filled.query(Song).count() == 3, "Database should be empty at the beginning of this test."

    # Add a song to the database in this session
    song = Song(name="Test Song", author="Test Author", times_used=0, cover_src="http://example.com/cover.jpg", audio_src="http://example.com/audio.mp3")
    db_session_filled.add(song)
    db_session_filled.commit()
    
    # Check if the song is in the database
    result = db_session_filled.query(Song).filter_by(name="Test Song").first()
    assert result is not None, "The song should be present in the database in this session."

def test_session_isolation_other_filled(db_session_filled: Session):
    """Test to ensure that changes in one session do not affect another session."""
    
    # Check if the database is empty at the beginning of the test
    assert db_session_filled.query(Song).count() == 3, "Database should be empty at the beginning of this test."

    # Check that the previous test did not affect this session
    result = db_session_filled.query(Song).filter_by(name="Test Song").first()
    assert result is None, "The song should not be present in this session if isolation is correct."
