import pytest

from api.exceptions.sessions.files import (FileDeleteError,
                                           FileExistsInSessionError,
                                           FileNotFoundInSessionError)
from api.services.files.occupied_slot import create, get, remove, update
from api.sessions.files import BaseFileSessionManager


# Create Tests
def test_create_occupied_slot_success(memory_file_session: BaseFileSessionManager):
    """Positiver Test: Erfolgreiches Erstellen einer neuen Datei in 'occupied_slots'."""
    new_slot_id = 999
    file_extension = "mp4"
    file_content = b"New slot content"

    # Act
    location = create(new_slot_id, file_extension, file_content, memory_file_session)

    # Assert
    assert location == f"memory://occupied_slots/{new_slot_id}.{file_extension}"

def test_create_occupied_slot_file_exists(memory_file_session: BaseFileSessionManager):
    """Negativer Test: Erstellen einer Datei, die bereits existiert in 'occupied_slots'."""
    existing_slot_id = 1  # Diese Datei existiert bereits
    file_extension = "mp4"
    file_content = b"New content"

    # Act & Assert
    with pytest.raises(FileExistsInSessionError):
        create(existing_slot_id, file_extension, file_content, memory_file_session)

# Get Tests
def test_get_occupied_slot_success(memory_file_session: BaseFileSessionManager):
    """Positiver Test: Erfolgreiches Abrufen einer existierenden Datei aus 'occupied_slots'."""
    slot_id = 1  # Diese Datei existiert bereits

    # Act
    retrieved_file = get(slot_id, memory_file_session)

    # Assert
    assert retrieved_file is not None
    assert isinstance(retrieved_file, bytes)

def test_get_occupied_slot_file_not_found(memory_file_session: BaseFileSessionManager):
    """Negativer Test: Abrufen einer Datei, die nicht existiert in 'occupied_slots'."""
    non_existing_slot_id = 999

    # Act & Assert
    with pytest.raises(FileNotFoundInSessionError):
        get(non_existing_slot_id, memory_file_session)

# Update Tests
def test_update_occupied_slot_success(memory_file_session: BaseFileSessionManager):
    """Positiver Test: Erfolgreiches Aktualisieren einer existierenden Datei in 'occupied_slots'."""
    existing_slot_id = 1
    new_file_content = b"Updated slot content"

    # Act
    updated_location = update(existing_slot_id, new_file_content, memory_file_session)

    # Assert
    assert updated_location == f"memory://occupied_slots/{existing_slot_id}.mp4"

def test_update_occupied_slot_file_not_found(memory_file_session: BaseFileSessionManager):
    """Negativer Test: Aktualisieren einer Datei, die nicht existiert in 'occupied_slots'."""
    non_existing_slot_id = 999
    new_file_content = b"Content for non-existing slot file"

    # Act & Assert
    with pytest.raises(FileNotFoundInSessionError):
        update(non_existing_slot_id, new_file_content, memory_file_session)

# Remove Tests
def test_remove_occupied_slot_success(memory_file_session: BaseFileSessionManager):
    """Positiver Test: Erfolgreiches Löschen einer existierenden Datei in 'occupied_slots'."""
    existing_slot_id = 1

    # Act
    remove(existing_slot_id, memory_file_session)

    # Assert: Nach dem Löschen sollte der Zugriff zu einem Fehler führen
    with pytest.raises(FileNotFoundInSessionError):
        get(existing_slot_id, memory_file_session)

def test_remove_occupied_slot_file_not_found(memory_file_session: BaseFileSessionManager):
    """Negativer Test: Löschen einer Datei, die nicht existiert in 'occupied_slots'."""
    non_existing_slot_id = 999

    # Act & Assert
    with pytest.raises(FileDeleteError):
        remove(non_existing_slot_id, memory_file_session)
