import pytest

from api.exceptions.sessions.files import FileNotFoundInSessionError
from api.services.files.demo_slot import get
from api.sessions.files import BaseFileSessionManager


def test_get_demo_success(memory_file_session: BaseFileSessionManager):
    """Positiver Test: Erfolgreiches Abrufen der Datei 'demo' aus 'demo_slot'."""
    # Act
    retrieved_file = get(memory_file_session)

    # Assert
    assert retrieved_file is not None
    assert isinstance(retrieved_file, bytes)

def test_get_demo_file_not_found(memory_file_session: BaseFileSessionManager):
    """Negativer Test: Abrufen einer nicht existierenden Datei in 'demo_slot'."""
    # Act: Leeren wir den Speicher oder löschen die Datei vor dem Zugriff
    memory_file_session.remove("demo", "demo_slot")

    # Act & Assert
    with pytest.raises(FileNotFoundInSessionError):
        get(memory_file_session)