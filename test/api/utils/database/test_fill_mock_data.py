from sqlalchemy.orm import Session
from api.models.database.model import Group, Song, User, Edit
from test.utils.test_model import test_model

def test_test_model_data_matches_db(db_session_filled: Session):
    # Daten aus der Datenbank abrufen
    groups_from_db = db_session_filled.query(Group).all()
    songs_from_db = db_session_filled.query(Song).all()
    users_from_db = db_session_filled.query(User).all()
    edits_from_db = db_session_filled.query(Edit).all()

    # Überprüfen, ob die Anzahl der Einträge stimmt
    assert len(groups_from_db) == len(test_model.groups)
    assert len(songs_from_db) == len(test_model.songs)
    assert len(users_from_db) == len(test_model.users)
    assert len(edits_from_db) == len(test_model.edits)

    # Überprüfen, ob die Daten inhaltlich übereinstimmen
    for expected_group, actual_group in zip(test_model.groups, groups_from_db):
        assert expected_group.group_id == actual_group.group_id
        assert expected_group.name == actual_group.name

    for expected_song, actual_song in zip(test_model.songs, songs_from_db):
        assert expected_song.song_id == actual_song.song_id
        assert expected_song.name == actual_song.name
        assert expected_song.author == actual_song.author
        assert expected_song.times_used == actual_song.times_used
        assert expected_song.cover_src == actual_song.cover_src
        assert expected_song.audio_src == actual_song.audio_src

    for expected_user, actual_user in zip(test_model.users, users_from_db):
        assert expected_user.user_id == actual_user.user_id
        assert expected_user.group_id == actual_user.group_id
        assert expected_user.role == actual_user.role
        assert expected_user.name == actual_user.name
        assert expected_user.email == actual_user.email

    for expected_edit, actual_edit in zip(test_model.edits, edits_from_db):
        assert expected_edit.edit_id == actual_edit.edit_id
        assert expected_edit.song_id == actual_edit.song_id
        assert expected_edit.created_by == actual_edit.created_by
        assert expected_edit.group_id == actual_edit.group_id
        assert expected_edit.name == actual_edit.name
        assert expected_edit.isLive == actual_edit.isLive
