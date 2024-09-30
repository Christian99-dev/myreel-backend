import pytest
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from api.models.database.model import Edit, Slot, Song
from api.services.database.song import (create, create_slots_from_breakpoints,
                                        get, get_breakpoints, get_earliest_slot_start_time, list_all, remove,
                                        update)
from mock.database.data import data

"""CRUD Operationen"""

# Create Tests
def test_create_success(memory_database_session: Session):
    # Arrange
    name = "Test Song"
    author = "Test Author"
    cover_src = "http://example.com/cover.jpg"
    audio_src = "http://example.com/audio.mp3"
    
    # Act
    new_song = create(name=name, author=author, cover_src=cover_src, audio_src=audio_src, database_session=memory_database_session)
    
    # Assert
    assert new_song is not None
    assert new_song.name == name
    assert new_song.author == author
    assert new_song.cover_src == cover_src
    assert new_song.audio_src == audio_src

def test_create_invalid_data(memory_database_session: Session):
    # Arrange
    name = None  # Invalid name (None)
    author = "Test Author"
    cover_src = "http://example.com/cover.jpg"
    audio_src = "http://example.com/audio.mp3"
    
    # Act & Assert
    with pytest.raises(IntegrityError):
        create(name=name, author=author, cover_src=cover_src, audio_src=audio_src, database_session=memory_database_session)

def test_create_edgecase_empty_name(memory_database_session: Session):
    # Arrange
    name = ""  # Empty name
    author = "Test Author"
    cover_src = "http://example.com/cover.jpg"
    audio_src = "http://example.com/audio.mp3"
    
    # Act
    new_song = create(name=name, author=author, cover_src=cover_src, audio_src=audio_src, database_session=memory_database_session)
    
    # Assert
    assert new_song is not None
    assert new_song.name == ""

# Get Tests
def test_get_success(memory_database_session: Session):
    # Arrange
    existing_song = data["songs"][0]
    
    # Act
    fetched_song = get(existing_song["song_id"], memory_database_session)
    
    # Assert
    assert fetched_song is not None
    assert fetched_song.song_id == existing_song["song_id"]

def test_get_invalid_id(memory_database_session: Session):
    # Arrange
    invalid_song_id = 9999
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        get(invalid_song_id, memory_database_session)

def test_get_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_song_id = 0
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        get(zero_song_id, memory_database_session)

# Update Tests
def test_update_success(memory_database_session: Session):
    # Arrange
    existing_song = data["songs"][0]
    new_name = "Updated Song"
    
    # Act
    updated_song = update(song_id=existing_song["song_id"], name=new_name, database_session=memory_database_session)
    
    # Assert
    assert updated_song is not None
    assert updated_song.name == new_name

def test_update_invalid_id(memory_database_session: Session):
    # Arrange
    invalid_song_id = 9999
    new_name = "Non-Existent Song"
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        update(song_id=invalid_song_id, name=new_name, database_session=memory_database_session)

def test_update_no_changes(memory_database_session: Session):
    # Arrange
    existing_song = data["songs"][0]
    
    # Act
    updated_song = update(song_id=existing_song["song_id"], database_session=memory_database_session)  # Keine Änderungen
    
    # Assert
    assert updated_song is not None
    assert updated_song.name == existing_song["name"]

# Remove Tests
def test_remove_success(memory_database_session: Session):
    # Arrange
    existing_song = memory_database_session.query(Song).first()
    
    # Act
    remove(existing_song.song_id, memory_database_session)
    
    # Assert
    with pytest.raises(NoResultFound):
        get(existing_song.song_id, memory_database_session)

def test_remove_invalid_id(memory_database_session: Session):
    # Arrange
    invalid_song_id = 9999
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        remove(invalid_song_id, memory_database_session)

def test_remove_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_song_id = 0
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        remove(zero_song_id, memory_database_session)


"""Andere Operationen"""

# list_all Tests
def test_list_all_success(memory_database_session: Session):
    # Act
    all_songs = list_all(memory_database_session)
    
    # Assert
    assert len(all_songs) == len(data["songs"])

def test_list_all_no_songs(memory_database_session: Session):
    # Arrange: Leere die Song-Datenbank
    memory_database_session.query(Song).delete()
    memory_database_session.commit()
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        list_all(memory_database_session)

# get_breakpoints Tests
def test_get_breakpoints_success(memory_database_session: Session):
    # Arrange
    song_id = 1  # Ein Song mit zugehörigen Slots
    
    # Act
    breakpoints = get_breakpoints(song_id, memory_database_session)
    
    # Assert
    assert breakpoints == [0.0, 0.5, 1.0, 2.0]

def test_get_breakpoints_no_slots(memory_database_session: Session):
    # Arrange
    song_id = 9999  # Keine Slots für diesen Song
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        get_breakpoints(song_id, memory_database_session)

def test_get_breakpoints_invalid_song_id(memory_database_session: Session):
    # Arrange
    invalid_song_id = 9999
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        get_breakpoints(invalid_song_id, memory_database_session)

# create_slots_from_breakpoints Tests
def test_create_slots_from_breakpoints_success(memory_database_session: Session):
    # Arrange
    song_id = 1
    breakpoints = [0.0, 1.0, 2.0, 3.0]
    
    # Act
    new_slots = create_slots_from_breakpoints(song_id, breakpoints, memory_database_session)
    
    # Assert
    assert len(new_slots) == 3  # 3 Slots should be created from 4 breakpoints

def test_create_slots_from_breakpoints_empty_list(memory_database_session: Session):
    # Arrange
    song_id = 1
    breakpoints = []  # Keine Breakpoints
    
    # Act & Assert
    with pytest.raises(ValueError):
        create_slots_from_breakpoints(song_id, breakpoints, memory_database_session)

def test_create_slots_from_breakpoints_too_few_breakpoints(memory_database_session: Session):
    # Arrange
    song_id = 1
    breakpoints = [0.0]  # Nicht genug Breakpoints
    
    # Act & Assert
    with pytest.raises(ValueError):
        create_slots_from_breakpoints(song_id, breakpoints, memory_database_session)

# get_earliest_slot_start_time
def test_get_earliest_slot_start_time_success(memory_database_session:Session):
    assert get_earliest_slot_start_time(1, memory_database_session) == 0
    assert get_earliest_slot_start_time(2, memory_database_session) == 0
    assert get_earliest_slot_start_time(3, memory_database_session) == 0.5
    
def test_get_earliest_slot_start_not_found(memory_database_session:Session):
    with pytest.raises(NoResultFound):
        get_earliest_slot_start_time(4, memory_database_session)

"""Integration - CRUD"""

def test_integration_crud_song(memory_database_session: Session):
    # Create a song
    new_song = create(name="Test Song", author="Test Author", cover_src="http://example.com/cover.jpg", audio_src="http://example.com/audio.mp3", database_session=memory_database_session)
    assert new_song is not None

    # Update the song
    updated_song = update(song_id=new_song.song_id, name="Updated Test Song", database_session=memory_database_session)
    assert updated_song is not None
    assert updated_song.name == "Updated Test Song"

    # Fetch the song and check the updated name
    fetched_song = get(song_id=new_song.song_id, database_session=memory_database_session)
    assert fetched_song is not None
    assert fetched_song.name == "Updated Test Song"

    # Remove the song
    remove(new_song.song_id, memory_database_session)

    # Ensure the song no longer exists
    with pytest.raises(NoResultFound):
        get(new_song.song_id, memory_database_session)


"""Integration - Cascading"""

def test_cascade_delete_song_with_slots_and_edits(memory_database_session: Session):
    # Arrange: Lösche einen Song und erwarte, dass alle zugehörigen Slots und Edits gelöscht werden.
    song_id = 1  # Ein Song mit zugehörigen Slots und Edits
    
    # Überprüfe, dass der Song existiert
    song = memory_database_session.query(Song).filter_by(song_id=song_id).one_or_none()
    assert song is not None

    # Überprüfe, dass zugehörige Slots existieren
    slots = memory_database_session.query(Slot).filter_by(song_id=song_id).all()
    assert len(slots) > 0

    # Überprüfe, dass zugehörige Edits existieren
    edits = memory_database_session.query(Edit).filter_by(song_id=song_id).all()
    assert len(edits) > 0

    # Act: Lösche den Song
    remove(song_id, memory_database_session)

    # Assert: Überprüfe, ob der Song erfolgreich gelöscht wurde
    with pytest.raises(NoResultFound):
        get(song_id, memory_database_session)

    # Überprüfe, dass alle zugehörigen Slots gelöscht wurden
    slots = memory_database_session.query(Slot).filter_by(song_id=song_id).all()
    assert len(slots) == 0

    # Überprüfe, dass alle zugehörigen Edits gelöscht wurden
    edits = memory_database_session.query(Edit).filter_by(song_id=song_id).all()
    assert len(edits) == 0
