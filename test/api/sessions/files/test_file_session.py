import pytest

from api.exceptions.sessions.files import (DirectoryNotFoundError,
                                           FileDeleteError,
                                           FileExistsInSessionError,
                                           FileNotFoundInSessionError)
from api.sessions.files import MemoryFileSessionManager


# Create Tests
def test_create_file_success(memory_file_session: MemoryFileSessionManager):
    # Erstelle eine neue Datei
    file_name = 'new_test_file.txt'
    directory = 'test_dir'
    file_data = b'Test content'
    
    result = memory_file_session.create(file_name, directory, file_data)
    assert result == f"memory://{directory}/{file_name}"
    assert memory_file_session.get(file_name, directory) == file_data

def test_create_file_duplicate(memory_file_session: MemoryFileSessionManager):
    # Versuche, eine bereits vorhandene Datei zu erstellen
    file_name = '1.mp4'
    directory = 'edits'
    file_data = b'Test content'

    with pytest.raises(FileExistsInSessionError):
        memory_file_session.create(file_name, directory, file_data)

def test_create_edgecase_empty_file_name(memory_file_session: MemoryFileSessionManager):
    # Teste das Erstellen einer Datei ohne Namen
    directory = 'test_dir'
    file_data = b'Test content'

    result = memory_file_session.create('', directory, file_data)
    assert result == f"memory://{directory}/"
    assert memory_file_session.get('', directory) == file_data


# Get Tests
def test_get_file_success(memory_file_session: MemoryFileSessionManager):
    # Hole eine bereits vorhandene Datei
    file_name = '1.mp4'
    directory = 'edits'

    assert memory_file_session.get(file_name, directory) is not None

def test_get_file_not_found(memory_file_session: MemoryFileSessionManager):
    # Versuche, eine nicht existierende Datei abzurufen
    with pytest.raises(FileNotFoundInSessionError):
        memory_file_session.get('non_existent_file.txt', 'test_dir')

def test_get_edgecase_empty_file_name(memory_file_session: MemoryFileSessionManager):
    # Teste das Abrufen einer Datei ohne Namen
    directory = 'test_dir'
    file_data = b'Test content'

    memory_file_session.create('', directory, file_data)
    assert memory_file_session.get('', directory) == file_data


# Update Tests
def test_update_file_success(memory_file_session: MemoryFileSessionManager):
    # Aktualisiere eine vorhandene Datei
    file_name = '1.mp4'
    directory = 'edits'
    new_file_data = b'Updated content'

    result = memory_file_session.update(file_name, directory, new_file_data)
    assert result == f"memory://{directory}/{file_name}"
    assert memory_file_session.get(file_name, directory) == new_file_data

def test_update_file_not_found(memory_file_session: MemoryFileSessionManager):
    # Versuche, eine nicht existierende Datei zu aktualisieren
    with pytest.raises(FileNotFoundInSessionError):
        memory_file_session.update('non_existent_file.txt', 'test_dir', b'New content')

def test_update_edgecase_empty_file_name(memory_file_session: MemoryFileSessionManager):
    # Aktualisiere eine Datei ohne Namen
    directory = 'test_dir'
    new_file_data = b'Updated content'

    memory_file_session.create('', directory, b'Initial content')
    result = memory_file_session.update('', directory, new_file_data)
    assert result == f"memory://{directory}/"
    assert memory_file_session.get('', directory) == new_file_data


# Remove Tests
def test_remove_file_success(memory_file_session: MemoryFileSessionManager):
    # Entferne eine vorhandene Datei
    file_name = '1.mp4'
    directory = 'edits'

    memory_file_session.remove(directory, file_name)
    with pytest.raises(FileNotFoundInSessionError):
        memory_file_session.get(file_name, directory)

def test_remove_file_not_found(memory_file_session: MemoryFileSessionManager):
    # Versuche, eine nicht existierende Datei zu entfernen
    with pytest.raises(FileDeleteError):
        memory_file_session.remove('test_dir', 'non_existent_file.txt')

def test_remove_edgecase_empty_file_name(memory_file_session: MemoryFileSessionManager):
    # Entferne eine Datei ohne Namen
    directory = 'test_dir'

    memory_file_session.create('', directory, b'File with empty name')
    memory_file_session.remove(directory, '')
    with pytest.raises(FileNotFoundInSessionError):
        memory_file_session.get('', directory)


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
    memory_file_session.create('test_file.txt', '', b'File in root directory')
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
