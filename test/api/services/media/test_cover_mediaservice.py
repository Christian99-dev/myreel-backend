from api.services.files.cover import get, create, remove, update

# get
def test_get_cover_file_found(media_access_memory):
    cover_id = 1234  # Angenommene cover_id
    file_extension = 'png'  # Angenommene Dateierweiterung
    file_name = f"{cover_id}.{file_extension}"

    # Simuliere das Vorhandensein der Datei in MemoryMediaAccess
    media_access_memory.save(file_name, "covers", b"dummy_cover_data")  # Speichere Dummy-Daten

    # Ruft die get-Funktion auf
    result = get(cover_id, media_access_memory)

    # Überprüfe, ob die zurückgegebenen Daten korrekt sind
    assert result == b"dummy_cover_data"

def test_get_cover_file_not_found(media_access_memory):
    cover_id = 9999  # Angenommene nicht existierende cover_id

    # Überprüfen, ob None zurückgegeben wird, wenn die Datei nicht gefunden wird
    result = get(cover_id, media_access_memory)
    assert result is None

# create
def test_create_cover_file(media_access_memory):
    cover_id = 1234  # Angenommene cover_id
    file_extension = 'png'  # Angenommene Dateierweiterung
    file_data = b"dummy_cover_data"

    # Ruft die create-Funktion auf
    location = create(cover_id, file_extension, file_data, media_access_memory)

    # Überprüfe, ob die Datei erfolgreich erstellt wurde
    expected_file_name = f"{cover_id}.{file_extension}"
    assert expected_file_name in media_access_memory.list("covers")

    # Überprüfe, ob die Datei die erwarteten Daten hat
    result = media_access_memory.get(expected_file_name, "covers")
    assert result == file_data

# remove
def test_remove_cover_file_found(media_access_memory):
    cover_id = 1234  # Angenommene cover_id
    file_extension = 'png'  # Angenommene Dateierweiterung
    file_name = f"{cover_id}.{file_extension}"

    # Simuliere das Vorhandensein der Datei in MemoryMediaAccess
    media_access_memory.save(file_name, "covers", b"dummy_cover_data")  # Speichere Dummy-Daten

    # Ruft die remove-Funktion auf
    result = remove(cover_id, media_access_memory)

    # Überprüfe, ob die Datei erfolgreich entfernt wurde
    assert result is True
    assert file_name not in media_access_memory.list("covers")

def test_remove_cover_file_not_found(media_access_memory):
    cover_id = 9999  # Angenommene nicht existierende cover_id

    # Überprüfen, ob False zurückgegeben wird, wenn die Datei nicht gefunden wird
    result = remove(cover_id, media_access_memory)
    assert result is False

# update
def test_update_cover_file(media_access_memory):
    cover_id = 1234  # Angenommene cover_id
    initial_data = b"initial_cover_data"
    updated_data = b"updated_cover_data"
    file_extension = 'png'  # Angenommene Dateierweiterung

    # Erstelle die ursprüngliche Datei
    create(cover_id, file_extension, initial_data, media_access_memory)

    # Aktualisiere die Datei
    update(cover_id, file_extension, updated_data, media_access_memory)

    # Überprüfe, ob die Datei aktualisiert wurde
    retrieved_cover = get(cover_id, media_access_memory)
    assert retrieved_cover == updated_data
