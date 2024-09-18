import pytest

from api.exceptions.files import (FileDeleteError,
                                           FileExistsInSessionError,
                                           FileNotFoundInSessionError)
from api.services.files.edit import create, get, remove, update
from api.sessions.files import BaseFileSessionManager


# Create Tests
def test_create_edit_success(memory_file_session: BaseFileSessionManager):
    """Positiver Test: Erfolgreiches Erstellen einer neuen Datei in 'edits'."""
    new_edit_id = 999  # Diese Datei existiert noch nicht
    file_extension = "mp4"
    file_content = b"New edit content"

    # Act
    location = create(new_edit_id, file_extension, file_content, memory_file_session)

    # Assert
    assert location == f"memory://edits/{new_edit_id}.{file_extension}"

def test_create_edit_file_exists(memory_file_session: BaseFileSessionManager):
    """Negativer Test: Erstellen einer Datei, die bereits existiert in 'edits'."""
    existing_edit_id = 1  # Diese Datei existiert bereits
    file_extension = "mp4"
    file_content = b"New content"

    # Act & Assert
    with pytest.raises(FileExistsInSessionError):
        create(existing_edit_id, file_extension, file_content, memory_file_session)

# Get Tests
def test_get_edit_success(memory_file_session: BaseFileSessionManager):
    """Positiver Test: Erfolgreiches Abrufen einer existierenden Datei aus 'edits'."""
    edit_id = 1  # Diese Datei existiert bereits

    # Act
    retrieved_file = get(edit_id, memory_file_session)

    # Assert
    assert retrieved_file is not None
    assert isinstance(retrieved_file, bytes)

def test_get_edit_file_not_found(memory_file_session: BaseFileSessionManager):
    """Negativer Test: Abrufen einer Datei, die nicht existiert in 'edits'."""
    non_existing_edit_id = 999  # Diese Datei existiert nicht

    # Act & Assert
    with pytest.raises(FileNotFoundInSessionError):
        get(non_existing_edit_id, memory_file_session)

# Update Tests
def test_update_edit_success(memory_file_session: BaseFileSessionManager):
    """Positiver Test: Erfolgreiches Aktualisieren einer existierenden Datei in 'edits'."""
    existing_edit_id = 1  # Diese Datei existiert bereits
    new_file_content = b"Updated edit content"

    # Act
    updated_location = update(existing_edit_id, new_file_content, memory_file_session)

    # Assert
    assert updated_location == f"memory://edits/{existing_edit_id}.mp4"

def test_update_edit_file_not_found(memory_file_session: BaseFileSessionManager):
    """Negativer Test: Aktualisieren einer Datei, die nicht existiert in 'edits'."""
    non_existing_edit_id = 999
    new_file_content = b"Content for non-existing edit file"

    # Act & Assert
    with pytest.raises(FileNotFoundInSessionError):
        update(non_existing_edit_id, new_file_content, memory_file_session)

# Remove Tests
def test_remove_edit_success(memory_file_session: BaseFileSessionManager):
    """Positiver Test: Erfolgreiches Löschen einer existierenden Datei in 'edits'."""
    existing_edit_id = 1  # Diese Datei existiert bereits

    # Act
    remove(existing_edit_id, memory_file_session)

    # Assert: Nach dem Löschen sollte der Zugriff zu einem Fehler führen
    with pytest.raises(FileNotFoundInSessionError):
        get(existing_edit_id, memory_file_session)

def test_remove_edit_file_not_found(memory_file_session: BaseFileSessionManager):
    """Negativer Test: Löschen einer Datei, die nicht existiert in 'edits'."""
    non_existing_edit_id = 999

    # Act & Assert
    with pytest.raises(FileDeleteError):
        remove(non_existing_edit_id, memory_file_session)
