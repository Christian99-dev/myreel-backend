import pytest

from api.exceptions.sessions.files import (FileDeleteError,
                                           FileExistsInSessionError,
                                           FileNotFoundInSessionError)
from api.services.files.cover import create, get, remove, update
from api.sessions.files import BaseFileSessionManager


# Create Tests
def test_create_success(memory_file_session: BaseFileSessionManager):
    """Positiver Test: Erfolgreiches Erstellen einer neuen Datei."""
    # Arrange
    new_song_id = 999  # Diese Datei existiert noch nicht
    file_extension = "png"
    file_content = b"New test content"

    # Act
    location = create(new_song_id, file_extension, file_content, memory_file_session)

    # Assert
    assert location == f"memory://covers/{new_song_id}.{file_extension}"

def test_create_file_exists(memory_file_session: BaseFileSessionManager):
    """Negativer Test: Erstellen einer Datei, die bereits existiert."""
    # Arrange
    existing_song_id = 1  # Diese Datei existiert bereits in der Session
    file_extension = "png"
    file_content = b"New test content"

    # Act & Assert
    with pytest.raises(FileExistsInSessionError):
        create(existing_song_id, file_extension, file_content, memory_file_session)

# Get Tests
def test_get_success(memory_file_session: BaseFileSessionManager):
    """Positiver Test: Erfolgreiches Abrufen einer existierenden Datei."""
    # Arrange
    song_id = 1  # Diese Datei existiert bereits in "covers"

    # Act
    retrieved_file = get(song_id, memory_file_session)

    # Assert
    assert retrieved_file is not None
    assert isinstance(retrieved_file, bytes)

def test_get_file_not_found(memory_file_session: BaseFileSessionManager):
    """Negativer Test: Abrufen einer Datei, die nicht existiert."""
    # Arrange
    non_existing_song_id = 999  # Diese Datei existiert nicht

    # Act & Assert
    with pytest.raises(FileNotFoundInSessionError):
        get(non_existing_song_id, memory_file_session)

# Update Tests
def test_update_success(memory_file_session: BaseFileSessionManager):
    """Positiver Test: Erfolgreiches Aktualisieren einer existierenden Datei."""
    # Arrange
    existing_song_id = 1  # Diese Datei existiert bereits
    new_file_content = b"Updated test content"

    # Act
    updated_location = update(existing_song_id, new_file_content, memory_file_session)

    # Assert
    assert updated_location == f"memory://covers/{existing_song_id}.png"

def test_update_file_not_found(memory_file_session: BaseFileSessionManager):
    """Negativer Test: Aktualisieren einer Datei, die nicht existiert."""
    # Arrange
    non_existing_song_id = 999  # Diese Datei existiert nicht
    new_file_content = b"Content for non-existing file"

    # Act & Assert
    with pytest.raises(FileNotFoundInSessionError):
        update(non_existing_song_id, new_file_content, memory_file_session)

# Remove Tests
def test_remove_success(memory_file_session: BaseFileSessionManager):
    """Positiver Test: Erfolgreiches Löschen einer existierenden Datei."""
    # Arrange
    existing_song_id = 1  # Diese Datei existiert bereits

    # Act
    remove(existing_song_id, memory_file_session)

    # Assert: Nach dem Löschen sollte der Zugriff zu einem Fehler führen
    with pytest.raises(FileNotFoundInSessionError):
        get(existing_song_id, memory_file_session)

def test_remove_file_not_found(memory_file_session: BaseFileSessionManager):
    """Negativer Test: Löschen einer Datei, die nicht existiert."""
    # Arrange
    non_existing_song_id = 999  # Diese Datei existiert nicht

    # Act & Assert
    with pytest.raises(FileDeleteError):
        remove(non_existing_song_id, memory_file_session)
