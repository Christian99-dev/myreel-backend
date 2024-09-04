
from api.services.files.song import get, create, remove


# get
def test_get_file_found(media_access_memory):
    song_id = 1234  # Angenommene song_id
    file_extension = 'mp3'  # Angenommene Dateierweiterung
    file_name = f"{song_id}.{file_extension}"

    # Simuliere das Vorhandensein der Datei in MemoryMediaAccess
    media_access_memory.save(file_name, "songs", b"dummy_audio_data")  # Speichere Dummy-Daten

    # Ruft die get-Funktion auf
    result = get(song_id, media_access_memory)

    # Überprüfe, ob die zurückgegebenen Daten korrekt sind
    assert result == b"dummy_audio_data"

def test_get_file_not_found(media_access_memory):
    song_id = 9999  # Angenommene nicht existierende song_id

    # Überprüfen, ob None zurückgegeben wird, wenn die Datei nicht gefunden wird
    result = get(song_id, media_access_memory)
    assert result is None

# create
def test_create_file(media_access_memory):
    song_id = 5678  # Angenommene song_id
    file_extension = 'wav'  # Angenommene Dateierweiterung
    file_data = b"dummy_audio_data_wav"

    # Ruft die create-Funktion auf
    location = create(song_id, file_extension, file_data, media_access_memory)

    # Überprüfe, ob die Datei erfolgreich erstellt wurde
    expected_file_name = f"{song_id}.{file_extension}"
    assert expected_file_name in media_access_memory.list("songs")

    # Überprüfe, ob die Datei die erwarteten Daten hat
    result = media_access_memory.get(expected_file_name, "songs")
    assert result == file_data
    
# remove
def test_remove_file_found(media_access_memory):
    song_id = 1234  # Angenommene song_id
    file_extension = 'mp3'  # Angenommene Dateierweiterung
    file_name = f"{song_id}.{file_extension}"

    # Simuliere das Vorhandensein der Datei in MemoryMediaAccess
    media_access_memory.save(file_name, "songs", b"dummy_audio_data")  # Speichere Dummy-Daten

    # Ruft die remove-Funktion auf
    result = remove(song_id, media_access_memory)

    # Überprüfe, ob die Datei erfolgreich entfernt wurde
    assert result is True
    assert file_name not in media_access_memory.list("songs")

def test_remove_file_not_found(media_access_memory):
    song_id = 9999  # Angenommene nicht existierende song_id

    # Überprüfen, ob False zurückgegeben wird, wenn die Datei nicht gefunden wird
    result = remove(song_id, media_access_memory)
    assert result is False