from sqlalchemy.orm import Session
from api.services.database.song import create, get_breakpoints, list_all, get, update, remove
from api.models.database.model import Song, Slot, Edit
from api.mock.database.model import mock_model_memory_links

# create
def test_create(db_memory: Session):
    # Arrange: Set up the parameters for the new song
    name = "Test Song"
    author = "Test Author"
    cover_src = "http://example.com/cover.jpg"
    audio_src = "http://example.com/audio.mp3"

    # Act: Call the create service function
    new_song = create(name, author, cover_src, audio_src, db_memory)
    
    # Assert: Check the created song's attributes
    assert new_song.name == name
    assert new_song.author == author
    assert new_song.cover_src == cover_src
    assert new_song.audio_src == audio_src
    assert new_song.times_used == 0

    # Verify: Ensure the song was actually added to the database
    song_in_db = db_memory.query(Song).filter_by(song_id=new_song.song_id).one_or_none()
    assert song_in_db is not None
    assert song_in_db.name == name
    assert song_in_db.author == author
    assert song_in_db.cover_src == cover_src
    assert song_in_db.audio_src == audio_src

# get
def test_get(db_memory: Session):
    # Assume the first song from the test data is used
    song_id = mock_model_memory_links.songs[0].song_id
    retrieved_song = get(song_id, db_memory)
    
    assert retrieved_song is not None
    assert retrieved_song.song_id == song_id
    assert retrieved_song.name == mock_model_memory_links.songs[0].name

# list
def test_list(db_memory: Session):
    songs = list_all(db_memory)
    
    assert len(songs) == len(mock_model_memory_links.songs)  # Ensure all test songs are present
    song_ids = {song.song_id for song in mock_model_memory_links.songs}
    retrieved_song_ids = {song.song_id for song in songs}
    assert song_ids == retrieved_song_ids  # Ensure all test song IDs are returned

# update
def test_update(db_memory: Session):
    # Assume the first song from the test data is used
    original_song = mock_model_memory_links.songs[0]
    song_id = original_song.song_id
    
    # Update parameters
    new_name = "Updated Song Name"
    new_author = "Updated Author"
    new_cover_src = "http://example.com/updated_cover.jpg"
    
    # Act: Call the update_song service function
    updated_song = update(
        song_id=song_id,
        name=new_name,
        author=new_author,
        cover_src=new_cover_src,
        db_session=db_memory
    )
    
    # Assert: Check that the song was updated correctly
    assert updated_song is not None
    assert updated_song.song_id == song_id
    assert updated_song.name == new_name
    assert updated_song.author == new_author
    assert updated_song.cover_src == new_cover_src
    assert updated_song.audio_src == original_song.audio_src  # Ensure unchanged fields are still correct

    # Verify: Ensure the updated song is actually saved in the database
    song_in_db = db_memory.query(Song).filter_by(song_id=song_id).one_or_none()
    assert song_in_db is not None
    assert song_in_db.name == new_name
    assert song_in_db.author == new_author
    assert song_in_db.cover_src == new_cover_src
    assert song_in_db.audio_src == original_song.audio_src

def test_update_song_not_found(db_memory: Session):
    # Arrange: Set up a non-existing song ID
    non_existing_song_id = 99999
    
    # Act: Try to update a song that doesn't exist
    updated_song = update(
        song_id=non_existing_song_id,
        name="New Name",
        db_session=db_memory
    )
    
    # Assert: Ensure that None is returned when the song doesn't exist
    assert updated_song is None

# remove
def test_remove_song(db_memory: Session):
    # Arrange: Verwende einen vorhandenen Song
    existing_song = db_memory.query(Song).first()

    # Act: Lösche den Song
    result = remove(existing_song.song_id, db_memory)

    # Assert: Überprüfe, dass der Song erfolgreich gelöscht wurde
    assert result is True

    # Verify: Stelle sicher, dass der Song nicht mehr in der Datenbank vorhanden ist
    song_in_db = db_memory.query(Song).filter_by(song_id=existing_song.song_id).one_or_none()
    assert song_in_db is None

    # cascading: Song -> Slot, Edit
    slots_in_db = db_memory.query(Slot).filter_by(song_id=existing_song.song_id).all()
    edits_in_db = db_memory.query(Edit).filter_by(song_id=existing_song.song_id).all()
    assert len(slots_in_db) == 0
    assert len(edits_in_db) == 0

def test_remove_song_failed(db_memory: Session):
    # Arrange: Verwende eine ungültige song_id
    non_existent_song_id = 9999

    # Act: Versuche, den Song mit der ungültigen ID zu löschen
    result = remove(non_existent_song_id, db_memory)

    # Assert: Stelle sicher, dass kein Song gelöscht wird
    assert result is False
    
# get breakpoints
def test_get_breakpoints_with_existing_slots(db_memory: Session):
    # Arrange: Verwende einen Song, der keine Slots hat
    song_id = mock_model_memory_links.songs[0].song_id  # Angenommen, der zweite Song hat keine Slots

    # Act: Hole die Breakpoints für den Song
    breakpoints = get_breakpoints(song_id, db_memory)

    # Assert: Überprüfe, dass eine leere Liste zurückgegeben wird
    expected_breakpoints = [0.0, 0.5, 1.0, 2.0]
    assert breakpoints == expected_breakpoints
    
    
    
    # Arrange: Verwende einen Song, der keine Slots hat
    song_id = mock_model_memory_links.songs[1].song_id  # Angenommen, der zweite Song hat keine Slots

    # Act: Hole die Breakpoints für den Song
    breakpoints = get_breakpoints(song_id, db_memory)

    # Assert: Überprüfe, dass eine leere Liste zurückgegeben wird
    expected_breakpoints = [0.0, 0.5, 1.5, 3.0]
    assert breakpoints == expected_breakpoints
    
    
    
    # Arrange: Verwende einen Song, der keine Slots hat
    song_id = mock_model_memory_links.songs[2].song_id  # Angenommen, der zweite Song hat keine Slots

    # Act: Hole die Breakpoints für den Song
    breakpoints = get_breakpoints(song_id, db_memory)

    # Assert: Überprüfe, dass eine leere Liste zurückgegeben wird
    expected_breakpoints = [0.5, 1.0, 2.0, 3.1, 3.3, 3.6, 3.8]
    assert breakpoints == expected_breakpoints
        
def test_get_breakpoints_with_no_slots(db_memory: Session):
    # Arrange: Erstelle einen Song und füge Slots mit Start- und Endzeiten hinzu
    song_id = mock_model_memory_links.songs[0].song_id
    
    # Arrange: Delete all breakpoints
    db_memory.query(Slot).filter(Slot.song_id == song_id).delete()
    db_memory.commit()

    # Act: Hole die Breakpoints für den Song
    breakpoints = get_breakpoints(song_id, db_memory)

    # Assert: Überprüfe die korrekten Breakpoints
    expected_breakpoints = []
    assert breakpoints == expected_breakpoints



def test_get_breakpoints_with_non_existing_song(db_memory: Session):
    # Arrange: Verwende eine nicht vorhandene Song-ID
    non_existing_song_id = 99999

    # Act: Hole die Breakpoints für den Song
    breakpoints = get_breakpoints(non_existing_song_id, db_memory)

    # Assert: Überprüfe, dass eine leere Liste zurückgegeben wird
    assert breakpoints == []
    
