from sqlalchemy.orm import Session
from api.models.database.model import Group, Song, User, Edit, Slot, Invitation, LoginRequest, OccupiedSlot
from test.utils.test_model import test_model

def test_test_model_data_matches_db(db_session_filled: Session):
    # Daten aus der Datenbank abrufen
    groups_from_db = db_session_filled.query(Group).all()
    songs_from_db = db_session_filled.query(Song).all()
    users_from_db = db_session_filled.query(User).all()
    edits_from_db = db_session_filled.query(Edit).all()
    slots_from_db = db_session_filled.query(Slot).all()
    invitations_from_db = db_session_filled.query(Invitation).all()
    login_requests_from_db = db_session_filled.query(LoginRequest).all()
    occupied_slots_from_db = db_session_filled.query(OccupiedSlot).all()

    # Überprüfen, ob die Anzahl der Einträge stimmt
    assert len(groups_from_db) == len(test_model.groups)
    assert len(songs_from_db) == len(test_model.songs)
    assert len(users_from_db) == len(test_model.users)
    assert len(edits_from_db) == len(test_model.edits)
    assert len(slots_from_db) == len(test_model.slots)
    assert len(invitations_from_db) == len(test_model.invitations)
    assert len(login_requests_from_db) == len(test_model.login_requests)
    assert len(occupied_slots_from_db) == len(test_model.occupied_slots)

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
        assert expected_edit.video_src == actual_edit.video_src

    for expected_slot, actual_slot in zip(test_model.slots, slots_from_db):
        assert expected_slot.slot_id == actual_slot.slot_id
        assert expected_slot.song_id == actual_slot.song_id
        assert expected_slot.start_time == actual_slot.start_time
        assert expected_slot.end_time == actual_slot.end_time

    for expected_invitation, actual_invitation in zip(test_model.invitations, invitations_from_db):
        assert expected_invitation.invitation_id == actual_invitation.invitation_id
        assert expected_invitation.group_id == actual_invitation.group_id
        assert expected_invitation.token == actual_invitation.token
        assert expected_invitation.email == actual_invitation.email
        assert expected_invitation.created_at == actual_invitation.created_at
        assert expected_invitation.expires_at == actual_invitation.expires_at

    for expected_login_request, actual_login_request in zip(test_model.login_requests, login_requests_from_db):
        assert expected_login_request.user_id == actual_login_request.user_id
        assert expected_login_request.pin == actual_login_request.pin
        assert expected_login_request.created_at == actual_login_request.created_at
        assert expected_login_request.expires_at == actual_login_request.expires_at

    for expected_occupied_slot, actual_occupied_slot in zip(test_model.occupied_slots, occupied_slots_from_db):
        assert expected_occupied_slot.user_id == actual_occupied_slot.user_id
        assert expected_occupied_slot.slot_id == actual_occupied_slot.slot_id
        assert expected_occupied_slot.edit_id == actual_occupied_slot.edit_id
        assert expected_occupied_slot.video_src == actual_occupied_slot.video_src
