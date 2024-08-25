from sqlalchemy.orm import Session
from api.services.database.song import create, list_all, get
from api.models.database.model import Song
from api.mock.database.model import model

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
    song_id = model.songs[0].song_id
    retrieved_song = get(song_id, db_memory)
    
    assert retrieved_song is not None
    assert retrieved_song.song_id == song_id
    assert retrieved_song.name == model.songs[0].name

# list
def test_list(db_memory: Session):
    songs = list_all(db_memory)
    
    assert len(songs) == len(model.songs)  # Ensure all test songs are present
    song_ids = {song.song_id for song in model.songs}
    retrieved_song_ids = {song.song_id for song in songs}
    assert song_ids == retrieved_song_ids  # Ensure all test song IDs are returned
