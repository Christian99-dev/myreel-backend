from api.services.files.cover import create, get, remove, update


# get
def test_get_cover_file_found(memory_file_session):
    cover_id = 1234  # Angenommene cover_id
    file_extension = 'png'  # Angenommene Dateierweiterung
    file_name = f"{cover_id}.{file_extension}"

    # Simuliere das Vorhandensein der Datei in MemoryMediaAccess
    memory_file_session.save(file_name, "covers", b"dummy_cover_data")  # Speichere Dummy-Daten

    # Ruft die get-Funktion auf
    result = get(cover_id, memory_file_session)

    # Überprüfe, ob die zurückgegebenen Daten korrekt sind
    assert result == b"dummy_cover_data"

def test_get_cover_file_not_found(memory_file_session):
    cover_id = 9999  # Angenommene nicht existierende cover_id

    # Überprüfen, ob None zurückgegeben wird, wenn die Datei nicht gefunden wird
    result = get(cover_id, memory_file_session)
    assert result is None

# create
def test_create_cover_file(memory_file_session):
    cover_id = 1234  # Angenommene cover_id
    file_extension = 'png'  # Angenommene Dateierweiterung
    file_data = b"dummy_cover_data"

    # Ruft die create-Funktion auf
    location = create(cover_id, file_extension, file_data, memory_file_session)

    # Überprüfe, ob die Datei erfolgreich erstellt wurde
    expected_file_name = f"{cover_id}.{file_extension}"
    assert expected_file_name in memory_file_session.list("covers")

    # Überprüfe, ob die Datei die erwarteten Daten hat
    result = memory_file_session.get(expected_file_name, "covers")
    assert result == file_data

# remove
def test_remove_cover_file_found(memory_file_session):
    cover_id = 1234  # Angenommene cover_id
    file_extension = 'png'  # Angenommene Dateierweiterung
    file_name = f"{cover_id}.{file_extension}"

    # Simuliere das Vorhandensein der Datei in MemoryMediaAccess
    memory_file_session.save(file_name, "covers", b"dummy_cover_data")  # Speichere Dummy-Daten

    # Ruft die remove-Funktion auf
    result = remove(cover_id, memory_file_session)

    # Überprüfe, ob die Datei erfolgreich entfernt wurde
    assert result is True
    assert file_name not in memory_file_session.list("covers")

def test_remove_cover_file_not_found(memory_file_session):
    cover_id = 9999  # Angenommene nicht existierende cover_id

    # Überprüfen, ob False zurückgegeben wird, wenn die Datei nicht gefunden wird
    result = remove(cover_id, memory_file_session)
    assert result is False

# update
def test_update_cover_file(memory_file_session):
    cover_id = 1234  # Angenommene cover_id
    initial_data = b"initial_cover_data"
    updated_data = b"updated_cover_data"
    file_extension = 'png'  # Angenommene Dateierweiterung

    # Erstelle die ursprüngliche Datei
    create(cover_id, file_extension, initial_data, memory_file_session)

    # Aktualisiere die Datei
    update(cover_id, file_extension, updated_data, memory_file_session)

    # Überprüfe, ob die Datei aktualisiert wurde
    retrieved_cover = get(cover_id, memory_file_session)
    assert retrieved_cover == updated_data
