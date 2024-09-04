from api.services.files.edit import get, create, remove, update

# get
def test_get_edit_file_found(media_access_memory):
    edit_id = 5678  # Angenommene edit_id
    file_extension = 'mp3'  # Angenommene Dateierweiterung
    file_name = f"{edit_id}.{file_extension}"

    # Simuliere das Vorhandensein der Datei in MemoryMediaAccess
    media_access_memory.save(file_name, "edits", b"dummy_edit_data")  # Speichere Dummy-Daten

    # Ruft die get-Funktion auf
    result = get(edit_id, media_access_memory)

    # Überprüfe, ob die zurückgegebenen Daten korrekt sind
    assert result == b"dummy_edit_data"

def test_get_edit_file_not_found(media_access_memory):
    edit_id = 9999  # Angenommene nicht existierende edit_id

    # Überprüfen, ob None zurückgegeben wird, wenn die Datei nicht gefunden wird
    result = get(edit_id, media_access_memory)
    assert result is None

# create
def test_create_edit_file(media_access_memory):
    edit_id = 5678  # Angenommene edit_id
    file_extension = 'mp3'  # Angenommene Dateierweiterung
    file_data = b"dummy_edit_data"

    # Ruft die create-Funktion auf
    location = create(edit_id, file_extension, file_data, media_access_memory)

    # Überprüfe, ob die Datei erfolgreich erstellt wurde
    expected_file_name = f"{edit_id}.{file_extension}"
    assert expected_file_name in media_access_memory.list("edits")

    # Überprüfe, ob die Datei die erwarteten Daten hat
    result = media_access_memory.get(expected_file_name, "edits")
    assert result == file_data

# remove
def test_remove_edit_file_found(media_access_memory):
    edit_id = 5678  # Angenommene edit_id
    file_extension = 'mp3'  # Angenommene Dateierweiterung
    file_name = f"{edit_id}.{file_extension}"

    # Simuliere das Vorhandensein der Datei in MemoryMediaAccess
    media_access_memory.save(file_name, "edits", b"dummy_edit_data")  # Speichere Dummy-Daten

    # Ruft die remove-Funktion auf
    result = remove(edit_id, media_access_memory)

    # Überprüfe, ob die Datei erfolgreich entfernt wurde
    assert result is True
    assert file_name not in media_access_memory.list("edits")

def test_remove_edit_file_not_found(media_access_memory):
    edit_id = 9999  # Angenommene nicht existierende edit_id

    # Überprüfen, ob False zurückgegeben wird, wenn die Datei nicht gefunden wird
    result = remove(edit_id, media_access_memory)
    assert result is False

# update
def test_update_edit_file(media_access_memory):
    edit_id = 5678
    initial_data = b"initial_edit_data"
    update_data = b"updated_edit_data"
    file_extension = 'mp3'

    # Erstelle die ursprüngliche Datei
    create(edit_id, file_extension, initial_data, media_access_memory)
    
    # Update die Datei
    update(edit_id, file_extension, update_data, media_access_memory)

    # Überprüfe, ob die Datei aktualisiert wurde
    retrieved_edit = get(edit_id, media_access_memory)
    assert retrieved_edit == update_data
