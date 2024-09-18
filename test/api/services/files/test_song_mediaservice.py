
from api.services.files.song import create, get, remove


# get
def test_get_file_found(memory_file_session):
    song_id = 1234  # Angenommene song_id
    file_extension = 'mp3'  # Angenommene Dateierweiterung
    file_name = f"{song_id}.{file_extension}"

    # Simuliere das Vorhandensein der Datei in MemoryMediaAccess
    memory_file_session.create(file_name, "songs", b"dummy_audio_data")  # Speichere Dummy-Daten

    # Ruft die get-Funktion auf
    result = get(song_id, memory_file_session)

    # Überprüfe, ob die zurückgegebenen Daten korrekt sind
    assert result == b"dummy_audio_data"

def test_get_file_not_found(memory_file_session):
    song_id = 9999  # Angenommene nicht existierende song_id

    # Überprüfen, ob None zurückgegeben wird, wenn die Datei nicht gefunden wird
    result = get(song_id, memory_file_session)
    assert result is None

# create
def test_create_file(memory_file_session):
    song_id = 5678  # Angenommene song_id
    file_extension = 'wav'  # Angenommene Dateierweiterung
    file_data = b"dummy_audio_data_wav"

    # Ruft die create-Funktion auf
    location = create(song_id, file_extension, file_data, memory_file_session)

    # Überprüfe, ob die Datei erfolgreich erstellt wurde
    expected_file_name = f"{song_id}.{file_extension}"
    assert expected_file_name in memory_file_session.list("songs")

    # Überprüfe, ob die Datei die erwarteten Daten hat
    result = memory_file_session.get(expected_file_name, "songs")
    assert result == file_data
    
# remove
def test_remove_file_found(memory_file_session):
    song_id = 1234  # Angenommene song_id
    file_extension = 'mp3'  # Angenommene Dateierweiterung
    file_name = f"{song_id}.{file_extension}"

    # Simuliere das Vorhandensein der Datei in MemoryMediaAccess
    memory_file_session.create(file_name, "songs", b"dummy_audio_data")  # Speichere Dummy-Daten

    # Ruft die remove-Funktion auf
    result = remove(song_id, memory_file_session)

    # Überprüfe, ob die Datei erfolgreich entfernt wurde
    assert result is True
    assert file_name not in memory_file_session.list("songs")

def test_remove_file_not_found(memory_file_session):
    song_id = 9999  # Angenommene nicht existierende song_id

    # Überprüfen, ob False zurückgegeben wird, wenn die Datei nicht gefunden wird
    result = remove(song_id, memory_file_session)
    assert result is False