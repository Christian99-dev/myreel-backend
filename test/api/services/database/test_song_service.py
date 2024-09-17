import logging
from sqlalchemy.orm import Session

from api.models.database.model import Edit, Slot, Song
from api.services.database.song import (create, create_slots_from_breakpoints,
                                        get, get_breakpoints, list_all, remove,
                                        update)
from mock.database.data import data

logger = logging.getLogger("test.unittest")

# create
def test_create(memory_database_session: Session):
    # Arrange: Set up the parameters for the new song
    name = "Test Song"
    author = "Test Author"
    cover_src = "http://example.com/cover.jpg"
    audio_src = "http://example.com/audio.mp3"

    # Act: Call the create service function
    new_song = create(name, author, cover_src, audio_src, memory_database_session)
    
    # Assert: Check the created song's attributes
    assert new_song.name == name
    assert new_song.author == author
    assert new_song.cover_src == cover_src
    assert new_song.audio_src == audio_src
    assert new_song.times_used == 0

    # Verify: Ensure the song was actually added to the database
    song_in_database_session = memory_database_session.query(Song).filter_by(song_id=new_song.song_id).one_or_none()
    assert song_in_database_session is not None
    assert song_in_database_session.name == name
    assert song_in_database_session.author == author
    assert song_in_database_session.cover_src == cover_src
    assert song_in_database_session.audio_src == audio_src

# get
def test_get(memory_database_session: Session):
    # Assume the first song from the test data is used
    song_id = data["songs"][0]["song_id"]
    retrieved_song = get(song_id, memory_database_session)
    
    assert retrieved_song is not None
    assert retrieved_song.song_id == song_id
    assert retrieved_song.name == data["songs"][0]["name"]

# list
def test_list(memory_database_session: Session):
    songs = list_all(memory_database_session)
    
    assert len(songs) == len(data["songs"])  # Ensure all test songs are present
    song_ids = {song["song_id"] for song in data["songs"]}
    retrieved_song_ids = {song.song_id for song in songs}
    assert song_ids == retrieved_song_ids  # Ensure all test song IDs are returned

# update
def test_update(memory_database_session: Session):
    # Assume the first song from the test data is used
    original_song = data["songs"][0]
    song_id = original_song["song_id"]
    
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
        db_session=memory_database_session
    )
    
    # Assert: Check that the song was updated correctly
    assert updated_song is not None
    assert updated_song.song_id == song_id
    assert updated_song.name == new_name
    assert updated_song.author == new_author
    assert updated_song.cover_src == new_cover_src
    assert updated_song.audio_src == original_song["audio_src"]  # Ensure unchanged fields are still correct

    # Verify: Ensure the updated song is actually saved in the database
    song_in_database_session = memory_database_session.query(Song).filter_by(song_id=song_id).one_or_none()
    assert song_in_database_session is not None
    assert song_in_database_session.name == new_name
    assert song_in_database_session.author == new_author
    assert song_in_database_session.cover_src == new_cover_src
    assert song_in_database_session.audio_src == original_song["audio_src"]

def test_update_song_not_found(memory_database_session: Session):
    # Arrange: Set up a non-existing song ID
    non_existing_song_id = 99999
    
    # Act: Try to update a song that doesn't exist
    updated_song = update(
        song_id=non_existing_song_id,
        name="New Name",
        db_session=memory_database_session
    )
    
    # Assert: Ensure that None is returned when the song doesn't exist
    assert updated_song is None

# remove
def test_remove_song(memory_database_session: Session):
    # Arrange: Verwende einen vorhandenen Song
    existing_song = memory_database_session.query(Song).first()

    # Act: Lösche den Song
    result = remove(existing_song.song_id, memory_database_session)

    # Assert: Überprüfe, dass der Song erfolgreich gelöscht wurde
    assert result is True

    # Verify: Stelle sicher, dass der Song nicht mehr in der Datenbank vorhanden ist
    song_in_database_session = memory_database_session.query(Song).filter_by(song_id=existing_song.song_id).one_or_none()
    assert song_in_database_session is None

    # cascading: Song -> Slot, Edit
    slots_in_database_session = memory_database_session.query(Slot).filter_by(song_id=existing_song.song_id).all()
    edits_in_database_session = memory_database_session.query(Edit).filter_by(song_id=existing_song.song_id).all()
    assert len(slots_in_database_session) == 0
    assert len(edits_in_database_session) == 0

def test_remove_song_failed(memory_database_session: Session):
    # Arrange: Verwende eine ungültige song_id
    non_existent_song_id = 9999

    # Act: Versuche, den Song mit der ungültigen ID zu löschen
    result = remove(non_existent_song_id, memory_database_session)

    # Assert: Stelle sicher, dass kein Song gelöscht wird
    assert result is False
    
# get breakpoints
def test_get_breakpoints_with_existing_slots(memory_database_session: Session):
    # Arrange: Verwende einen Song, der keine Slots hat
    song_id = data["songs"][0]["song_id"]  # Angenommen, der zweite Song hat keine Slots

    # Act: Hole die Breakpoints für den Song
    breakpoints = get_breakpoints(song_id, memory_database_session)

    # Assert: Überprüfe, dass eine leere Liste zurückgegeben wird
    expected_breakpoints = [0.0, 0.5, 1.0, 2.0]
    assert breakpoints == expected_breakpoints
    
    
    
    # Arrange: Verwende einen Song, der keine Slots hat
    song_id = data["songs"][1]["song_id"]  # Angenommen, der zweite Song hat keine Slots

    # Act: Hole die Breakpoints für den Song
    breakpoints = get_breakpoints(song_id, memory_database_session)

    # Assert: Überprüfe, dass eine leere Liste zurückgegeben wird
    expected_breakpoints = [0.0, 0.5, 1.5, 3.0]
    assert breakpoints == expected_breakpoints
    
    
    
    # Arrange: Verwende einen Song, der keine Slots hat
    song_id = data["songs"][2]["song_id"]  # Angenommen, der zweite Song hat keine Slots

    # Act: Hole die Breakpoints für den Song
    breakpoints = get_breakpoints(song_id, memory_database_session)

    # Assert: Überprüfe, dass eine leere Liste zurückgegeben wird
    expected_breakpoints = [0.5, 1.0, 2.0, 3.1, 3.3, 3.6, 3.8]
    assert breakpoints == expected_breakpoints
        
def test_get_breakpoints_with_no_slots(memory_database_session: Session):
    # Arrange: Erstelle einen Song und füge Slots mit Start- und Endzeiten hinzu
    song_id = data["songs"][0]["song_id"]
    
    # Arrange: Delete all breakpoints
    memory_database_session.query(Slot).filter(Slot.song_id == song_id).delete()
    memory_database_session.commit()

    # Act: Hole die Breakpoints für den Song
    breakpoints = get_breakpoints(song_id, memory_database_session)

    # Assert: Überprüfe die korrekten Breakpoints
    expected_breakpoints = []
    assert breakpoints == expected_breakpoints

def test_get_breakpoints_with_non_existing_song(memory_database_session: Session):
    # Arrange: Verwende eine nicht vorhandene Song-ID
    non_existing_song_id = 99999

    # Act: Hole die Breakpoints für den Song
    breakpoints = get_breakpoints(non_existing_song_id, memory_database_session)

    # Assert: Überprüfe, dass eine leere Liste zurückgegeben wird
    assert breakpoints == []
    
# create_slots_from_breakpoints    
def test_create_slots_from_breakpoints(memory_database_session: Session):
    # Arrange: Create song
    name = "Test Song"
    author = "Test Author"
    cover_src = "http://example.com/cover.jpg"
    audio_src = "http://example.com/audio.mp3"
    new_song = create(name, author, cover_src, audio_src, memory_database_session)
    song_id = new_song.song_id
    
    # Arrange: Breakpoints
    breakpoints = [0.0, 0.5, 1.0, 1.5, 2.0]  # Example breakpoints

    # Act: Call the create_slots_from_breakpoints function
    create_slots_from_breakpoints(song_id, breakpoints, memory_database_session)

    # Assert: Verify the slots were created correctly
    created_slots = memory_database_session.query(Slot).filter_by(song_id=song_id).all()
    
    # Check if the number of slots matches expected
    assert len(created_slots) == len(breakpoints) - 1  # Should create slots between breakpoints

    # Verify start and end times of each slot
    for i in range(len(breakpoints) - 1):
        assert created_slots[i].start_time == breakpoints[i]
        assert created_slots[i].end_time == breakpoints[i + 1]

def test_create_slots_from_empty_breakpoints(memory_database_session: Session):
    # Arrange: Create song
    name = "Test Song Empty"
    author = "Test Author"
    cover_src = "http://example.com/cover_empty.jpg"
    audio_src = "http://example.com/audio_empty.mp3"
    new_song = create(name, author, cover_src, audio_src, memory_database_session)
    song_id = new_song.song_id

    # Arrange: Empty breakpoints
    breakpoints = []  # Empty breakpoints

    # Act: Call the function
    create_slots_from_breakpoints(song_id, breakpoints, memory_database_session)

    # Assert: Ensure no slots were created
    created_slots = memory_database_session.query(Slot).filter_by(song_id=song_id).all()
    assert len(created_slots) == 0