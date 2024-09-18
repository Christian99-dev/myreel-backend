import pytest

from api.exceptions.files import (DirectoryNotFoundError, FileDeleteError,
                                  FileExistsInSessionError,
                                  FileNotFoundInSessionError)
from api.sessions.files import BaseFileSessionManager, MemoryFileSessionManager


# Create Tests
def test_create_success(memory_file_session: BaseFileSessionManager):
    """Testet das erfolgreiche Erstellen einer neuen Datei."""
    # Arrange: Nutze eine nicht-existierende Datei
    new_song_id = 999
    file_extension = "png"
    file_content = b"New test content"

    # Act
    location = memory_file_session.create(str(new_song_id), file_extension, file_content, "covers")
    
    # Assert
    assert location == f"memory://covers/{new_song_id}.{file_extension}"
    assert memory_file_session.get(str(new_song_id), "covers") == file_content

def test_create_file_exists(memory_file_session: BaseFileSessionManager):
    """Testet das Erstellen einer Datei, die bereits existiert."""
    # Arrange: Nutze eine bereits existierende Datei
    existing_song_id = 1
    file_extension = "png"
    file_content = b"New content"
    
    # Act & Assert: Creating the same file again should raise an error
    with pytest.raises(FileExistsInSessionError):
        memory_file_session.create(str(existing_song_id), file_extension, file_content, "covers")

def test_create_edge_case_empty_content(memory_file_session: BaseFileSessionManager):
    """Testet das Erstellen einer Datei mit leerem Inhalt."""
    # Arrange: Nutze eine neue Datei mit leerem Inhalt
    song_id = 1000
    file_extension = "png"
    empty_content = b""
    
    # Act
    location = memory_file_session.create(str(song_id), file_extension, empty_content, "covers")
    
    # Assert
    assert location == f"memory://covers/{song_id}.{file_extension}"
    assert memory_file_session.get(str(song_id), "covers") == empty_content

def test_create_edge_case_large_file(memory_file_session: BaseFileSessionManager):
    """Testet das Erstellen einer sehr großen Datei."""
    large_song_id = 9999
    file_extension = "png"
    large_file_content = b"A" * 10**6  # 1 MB große Datei
    
    # Act
    location = memory_file_session.create(str(large_song_id), file_extension, large_file_content, "covers")
    
    # Assert
    assert location == f"memory://covers/{large_song_id}.{file_extension}"
    assert memory_file_session.get(str(large_song_id), "covers") == large_file_content

# Get Tests
def test_get_success(memory_file_session: BaseFileSessionManager):
    """Testet das erfolgreiche Abrufen einer existierenden Datei."""
    # Arrange: Nutze eine existierende Datei
    song_id = 1
    
    # Act
    retrieved_file = memory_file_session.get(str(song_id), "covers")
    
    # Assert
    assert retrieved_file is not None
    assert isinstance(retrieved_file, bytes)

def test_get_file_not_found(memory_file_session: BaseFileSessionManager):
    """Testet das Abrufen einer Datei, die nicht existiert."""
    # Arrange: Nutze eine nicht-existierende Datei
    non_existing_song_id = 999
    
    # Act & Assert
    with pytest.raises(FileNotFoundInSessionError):
        memory_file_session.get(str(non_existing_song_id), "covers")

def test_get_edge_case_existing_empty_file(memory_file_session: BaseFileSessionManager):
    """Testet das Abrufen einer existierenden Datei mit leerem Inhalt."""
    # Arrange: Simuliere eine Datei mit leerem Inhalt
    song_id = 100
    empty_content = b""
    memory_file_session.create(str(song_id), "png", empty_content, "covers")
    
    # Act
    retrieved_file = memory_file_session.get(str(song_id), "covers")
    
    # Assert
    assert retrieved_file == empty_content

# Update Tests
def test_update_success(memory_file_session: BaseFileSessionManager):
    """Testet das erfolgreiche Aktualisieren einer existierenden Datei."""
    # Arrange: Nutze eine bereits existierende Datei
    existing_song_id = 1
    new_file_content = b"Updated content"
    
    # Act
    updated_location = memory_file_session.update(str(existing_song_id), new_file_content, "covers")
    
    # Assert
    assert updated_location == f"memory://covers/{existing_song_id}.png"
    assert memory_file_session.get(str(existing_song_id), "covers") == new_file_content

def test_update_file_not_found(memory_file_session: BaseFileSessionManager):
    """Testet das Aktualisieren einer Datei, die nicht existiert."""
    # Arrange: Nutze eine nicht-existierende Datei
    non_existing_song_id = 999
    new_file_content = b"Content for non-existing file"
    
    # Act & Assert
    with pytest.raises(FileNotFoundInSessionError):
        memory_file_session.update(str(non_existing_song_id), new_file_content, "covers")

def test_update_edge_case_empty_content(memory_file_session: BaseFileSessionManager):
    """Testet das Aktualisieren einer existierenden Datei mit leerem Inhalt."""
    # Arrange: Nutze eine existierende Datei und aktualisiere sie mit leerem Inhalt
    existing_song_id = 1
    empty_file_content = b""
    
    # Act
    updated_location = memory_file_session.update(str(existing_song_id), empty_file_content, "covers")
    
    # Assert
    assert updated_location == f"memory://covers/{existing_song_id}.png"
    assert memory_file_session.get(str(existing_song_id), "covers") == empty_file_content

# Remove Tests
def test_remove_success(memory_file_session: BaseFileSessionManager):
    """Testet das erfolgreiche Löschen einer existierenden Datei."""
    # Arrange: Nutze eine bereits existierende Datei
    existing_song_id = 1
    
    # Act
    memory_file_session.remove(str(existing_song_id), "covers")
    
    # Assert: Versuche, erneut zuzugreifen, sollte FileNotFoundInSessionError werfen
    with pytest.raises(FileNotFoundInSessionError):
        memory_file_session.get(str(existing_song_id), "covers")

def test_remove_file_not_found(memory_file_session: BaseFileSessionManager):
    """Testet das Löschen einer Datei, die nicht existiert."""
    # Arrange: Nutze eine nicht-existierende Datei
    non_existing_song_id = 999
    
    # Act & Assert
    with pytest.raises(FileDeleteError):
        memory_file_session.remove(str(non_existing_song_id), "covers")

def test_remove_edge_case_empty_directory(memory_file_session: BaseFileSessionManager):
    """Testet das Löschen einer Datei in einem leeren Verzeichnis."""
    # Arrange: Simuliere, dass das Verzeichnis leer ist
    memory_file_session.clear()
    
    # Act & Assert
    with pytest.raises(DirectoryNotFoundError):
        memory_file_session.remove(str(1), "covers")  # Versuche, eine Datei zu löschen, die nicht existiert

# Clear Tests
def test_clear_success(memory_file_session: MemoryFileSessionManager):
    # Leere den gesamten Speicher
    memory_file_session.clear()
    assert memory_file_session.list_all() == []

# List Tests
def test_list_files_success(memory_file_session: MemoryFileSessionManager):
    # Liste die Dateien in einem Verzeichnis auf
    directory = 'edits'
    files = memory_file_session.list(directory)
    assert len(files) == 9  # 9 Dateien im 'edits'-Ordner (aus dem Bild)

def test_list_directory_not_found(memory_file_session: MemoryFileSessionManager):
    # Versuche, ein nicht existierendes Verzeichnis aufzulisten
    with pytest.raises(DirectoryNotFoundError):
        memory_file_session.list('non_existent_dir')

def test_list_edgecase_empty_directory(memory_file_session: MemoryFileSessionManager):
    # Liste Dateien in einem leeren Verzeichnis auf
    memory_file_session.create('test_file',"txt", b'File in root directory', '',)
    files = memory_file_session.list('')
    assert 'test_file.txt' in files

# List All Tests
def test_list_all_files_success(memory_file_session: MemoryFileSessionManager):
    # Liste alle Dateien im Speicher auf
    all_files = memory_file_session.list_all()
    assert len(all_files) > 0  # Es sollten mehrere Dateien vorhanden sein

def test_list_all_after_clear(memory_file_session: MemoryFileSessionManager):
    # Liste alle Dateien auf, nachdem der Speicher geleert wurde
    memory_file_session.clear()
    all_files = memory_file_session.list_all()
    assert all_files == []
