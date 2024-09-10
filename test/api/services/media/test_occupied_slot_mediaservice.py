from api.services.files.occupied_slot import get, create, remove, update

# get
def test_get_occupied_slot_file_found(memory_file_session):
    slot_id = 1  # Angenommene slot_id
    file_extension = 'mp4'  # Angenommene Dateierweiterung
    file_name = f"{slot_id}.{file_extension}"

    # Simuliere das Vorhandensein der Datei in MemoryMediaAccess
    memory_file_session.save(file_name, "occupied_slots", b"dummy_slot_data")  # Speichere Dummy-Daten

    # Ruft die get-Funktion auf
    result = get(slot_id, memory_file_session)

    # Überprüfe, ob die zurückgegebenen Daten korrekt sind
    assert result == b"dummy_slot_data"

def test_get_occupied_slot_file_not_found(memory_file_session):
    slot_id = 9999  # Angenommene nicht existierende slot_id

    # Überprüfen, ob None zurückgegeben wird, wenn die Datei nicht gefunden wird
    result = get(slot_id, memory_file_session)
    assert result is None

# create
def test_create_occupied_slot_file(memory_file_session):
    slot_id = 1  # Angenommene slot_id
    file_extension = 'mp4'  # Angenommene Dateierweiterung
    file_data = b"dummy_slot_data"

    # Ruft die create-Funktion auf
    location = create(slot_id, file_extension, file_data, memory_file_session)

    # Überprüfe, ob die Datei erfolgreich erstellt wurde
    expected_file_name = f"{slot_id}.{file_extension}"
    assert expected_file_name in memory_file_session.list("occupied_slots")

    # Überprüfe, ob die Datei die erwarteten Daten hat
    result = memory_file_session.get(expected_file_name, "occupied_slots")
    assert result == file_data

# remove
def test_remove_occupied_slot_file_found(memory_file_session):
    slot_id = 1  # Angenommene slot_id
    file_extension = 'mp4'  # Angenommene Dateierweiterung
    file_name = f"{slot_id}.{file_extension}"

    # Simuliere das Vorhandensein der Datei in MemoryMediaAccess
    memory_file_session.save(file_name, "occupied_slots", b"dummy_slot_data")  # Speichere Dummy-Daten

    # Ruft die remove-Funktion auf
    result = remove(slot_id, memory_file_session)

    # Überprüfe, ob die Datei erfolgreich entfernt wurde
    assert result is True
    assert file_name not in memory_file_session.list("occupied_slots")

def test_remove_occupied_slot_file_not_found(memory_file_session):
    slot_id = 9999  # Angenommene nicht existierende slot_id

    # Überprüfen, ob False zurückgegeben wird, wenn die Datei nicht gefunden wird
    result = remove(slot_id, memory_file_session)
    assert result is False

# update
def test_update_occupied_slot_file(memory_file_session):
    slot_id = 1
    initial_data = b"initial_slot_data"
    update_data = b"updated_slot_data"
    file_extension = 'mp4'

    # Erstelle die ursprüngliche Datei
    create(slot_id, file_extension, initial_data, memory_file_session)

    # Update die Datei
    update(slot_id, file_extension, update_data, memory_file_session)

    # Überprüfe, ob die Datei aktualisiert wurde
    retrieved_slot = get(slot_id, memory_file_session)
    assert retrieved_slot == update_data
