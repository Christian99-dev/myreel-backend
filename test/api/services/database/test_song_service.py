import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.models.database.model import Edit, Slot, Song
from api.services.database.song import (create, create_slots_from_breakpoints,
                                        get, get_breakpoints, list_all, remove,
                                        update)
from mock.database.data import data

"""CRUD Operationen"""

# Create Tests
def test_create_success(memory_database_session: Session):
    # Arrange
    name = "New Song"
    author = "New Author"
    cover_src = "http://example.com/covers/new_cover.png"
    audio_src = "http://example.com/audios/new_audio.mp3"
    
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
    author = "New Author"
    cover_src = "http://example.com/covers/new_cover.png"
    audio_src = "http://example.com/audios/new_audio.mp3"
    
    # Act & Assert
    with pytest.raises(IntegrityError):
        create(name=name, author=author, cover_src=cover_src, audio_src=audio_src, database_session=memory_database_session)

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
    non_existent_song_id = 9999
    
    # Act
    fetched_song = get(non_existent_song_id, memory_database_session)
    
    # Assert
    assert fetched_song is None

def test_get_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_song_id = 0
    
    # Act
    fetched_song = get(zero_song_id, memory_database_session)
    
    # Assert
    assert fetched_song is None

# Update Tests
def test_update_success(memory_database_session: Session):
    # Arrange
    existing_song = data["songs"][0]
    new_name = "Updated Song Name"
    
    # Act
    updated_song = update(song_id=existing_song["song_id"], name=new_name, database_session=memory_database_session)
    
    # Assert
    assert updated_song is not None
    assert updated_song.name == new_name

def test_update_invalid_id(memory_database_session: Session):
    # Arrange
    non_existent_song_id = 9999
    new_name = "Non-Existent Song Update"
    
    # Act
    updated_song = update(song_id=non_existent_song_id, name=new_name, database_session=memory_database_session)
    
    # Assert
    assert updated_song is None

def test_update_edgecase_empty_name(memory_database_session: Session):
    # Arrange
    existing_song = data["songs"][0]
    new_name = ""  # Empty name
    
    # Act
    updated_song = update(song_id=existing_song["song_id"], name=new_name, database_session=memory_database_session)
    
    # Assert
    assert updated_song is not None
    assert updated_song.name == ""  # Empty name should be accepted

# Remove Tests
def test_remove_success(memory_database_session: Session):
    # Arrange
    existing_song = memory_database_session.query(Song).first()
    
    # Act
    result = remove(existing_song.song_id, memory_database_session)
    
    # Assert
    assert result is True
    assert memory_database_session.query(Song).filter_by(song_id=existing_song.song_id).one_or_none() is None

def test_remove_invalid_id(memory_database_session: Session):
    # Arrange
    non_existent_song_id = 9999
    
    # Act
    result = remove(non_existent_song_id, memory_database_session)
    
    # Assert
    assert result is False

def test_remove_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_song_id = 0
    
    # Act
    result = remove(zero_song_id, memory_database_session)
    
    # Assert
    assert result is False

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
    
    # Act
    all_songs = list_all(memory_database_session)
    
    # Assert
    assert len(all_songs) == 0

# get_breakpoints Tests
def test_get_breakpoints_success(memory_database_session: Session):
    # Arrange
    song_id = 1
    
    # Act
    breakpoints = get_breakpoints(song_id, memory_database_session)
    
    # Assert
    assert breakpoints == [0, 0.5, 1, 2]

def test_get_breakpoints_no_slots(memory_database_session: Session):
    # Arrange
    song_id = 1  # Song without any slots

    # Lösche alle Slots für den Song
    memory_database_session.query(Slot).filter(Slot.song_id == song_id).delete()
    memory_database_session.commit()
    
    # Act
    breakpoints = get_breakpoints(song_id, memory_database_session)
    
    # Assert
    assert breakpoints == []

# create_slots_from_breakpoints Tests
def test_create_slots_from_breakpoints_success(memory_database_session: Session):
    # Arrange
    song_id = 3
    breakpoints = [0.0, 1.0, 2.0, 3.0]
    
    # Act
    new_slots = create_slots_from_breakpoints(song_id, breakpoints, memory_database_session)
    
    # Assert
    assert len(new_slots) == 3  # 3 Slots should be created from 4 breakpoints
    assert new_slots[0].start_time == 0.0
    assert new_slots[0].end_time == 1.0
    assert new_slots[1].start_time == 1.0
    assert new_slots[1].end_time == 2.0
    assert new_slots[2].start_time == 2.0
    assert new_slots[2].end_time == 3.0

def test_create_slots_from_breakpoints_empty_list(memory_database_session: Session):
    # Arrange
    song_id = 3
    breakpoints = []  # No breakpoints provided
    
    # Act
    new_slots = create_slots_from_breakpoints(song_id, breakpoints, memory_database_session)
    
    # Assert
    assert len(new_slots) == 0  # No slots should be created

"""Integration"""

def test_cascade_delete_song_with_slots_and_edits(memory_database_session: Session):
    # Arrange: Wir löschen ein Lied und erwarten, dass alle zugehörigen Slots und Edits gelöscht werden.
    song_id = 1  # Song 1

    # Überprüfen, dass das Lied existiert
    song = memory_database_session.query(Song).filter_by(song_id=song_id).one_or_none()
    assert song is not None

    # Überprüfen, dass zugehörige Slots existieren
    slots = memory_database_session.query(Slot).filter_by(song_id=song_id).all()
    assert len(slots) > 0

    # Überprüfen, dass zugehörige Edits existieren
    edits = memory_database_session.query(Edit).filter_by(song_id=song_id).all()
    assert len(edits) > 0

    # Act: Lösche das Lied
    result = remove(song_id, memory_database_session)

    # Assert: Überprüfe, ob das Lied erfolgreich gelöscht wurde
    assert result is True
    song = memory_database_session.query(Song).filter_by(song_id=song_id).one_or_none()
    assert song is None

    # Überprüfen, dass alle zugehörigen Slots gelöscht wurden
    slots = memory_database_session.query(Slot).filter_by(song_id=song_id).all()
    assert len(slots) == 0

    # Überprüfen, dass alle zugehörigen Edits gelöscht wurden
    edits = memory_database_session.query(Edit).filter_by(song_id=song_id).all()
    assert len(edits) == 0