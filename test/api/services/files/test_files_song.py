import pytest

from api.exceptions.files import (FileDeleteError,
                                           FileExistsInSessionError,
                                           FileNotFoundInSessionError)
from api.services.files.song import create, get, remove, update
from api.sessions.files import BaseFileSessionManager


# Create Tests
def test_create_song_success(memory_file_session: BaseFileSessionManager):
    """Positiver Test: Erfolgreiches Erstellen einer neuen Datei in 'songs'."""
    new_song_id = 999
    file_extension = "wav"
    file_content = b"New song content"

    # Act
    location = create(new_song_id, file_extension, file_content, memory_file_session)

    # Assert
    assert location == f"memory://songs/{new_song_id}.{file_extension}"

def test_create_song_file_exists(memory_file_session: BaseFileSessionManager):
    """Negativer Test: Erstellen einer Datei, die bereits existiert in 'songs'."""
    existing_song_id = 1
    file_extension = "wav"
    file_content = b"New content"

    # Act & Assert
    with pytest.raises(FileExistsInSessionError):
        create(existing_song_id, file_extension, file_content, memory_file_session)

# Get Tests
def test_get_song_success(memory_file_session: BaseFileSessionManager):
    """Positiver Test: Erfolgreiches Abrufen einer existierenden Datei aus 'songs'."""
    song_id = 1  # Diese Datei existiert bereits

    # Act
    retrieved_file = get(song_id, memory_file_session)

    # Assert
    assert retrieved_file is not None
    assert isinstance(retrieved_file, bytes)

def test_get_song_file_not_found(memory_file_session: BaseFileSessionManager):
    """Negativer Test: Abrufen einer Datei, die nicht existiert in 'songs'."""
    non_existing_song_id = 999

    # Act & Assert
    with pytest.raises(FileNotFoundInSessionError):
        get(non_existing_song_id, memory_file_session)

# Update Tests
def test_update_song_success(memory_file_session: BaseFileSessionManager):
    """Positiver Test: Erfolgreiches Aktualisieren einer existierenden Datei in 'songs'."""
    existing_song_id = 1
    new_file_content = b"Updated song content"

    # Act
    updated_location = update(existing_song_id, new_file_content, memory_file_session)

    # Assert
    assert updated_location == f"memory://songs/{existing_song_id}.wav"

def test_update_song_file_not_found(memory_file_session: BaseFileSessionManager):
    """Negativer Test: Aktualisieren einer Datei, die nicht existiert in 'songs'."""
    non_existing_song_id = 999
    new_file_content = b"Content for non-existing song file"

    # Act & Assert
    with pytest.raises(FileNotFoundInSessionError):
        update(non_existing_song_id, new_file_content, memory_file_session)

# Remove Tests
def test_remove_song_success(memory_file_session: BaseFileSessionManager):
    """Positiver Test: Erfolgreiches Löschen einer existierenden Datei in 'songs'."""
    existing_song_id = 1

    # Act
    remove(existing_song_id, memory_file_session)

    # Assert: Nach dem Löschen sollte der Zugriff zu einem Fehler führen
    with pytest.raises(FileNotFoundInSessionError):
        get(existing_song_id, memory_file_session)

def test_remove_song_file_not_found(memory_file_session: BaseFileSessionManager):
    """Negativer Test: Löschen einer Datei, die nicht existiert in 'songs'."""
    non_existing_song_id = 999

    # Act & Assert
    with pytest.raises(FileDeleteError):
        remove(non_existing_song_id, memory_file_session)
