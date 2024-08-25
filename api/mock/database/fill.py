from sqlalchemy.orm import Session
from api.models.database.model import Group, Song, User, Edit, Slot, Invitation, LoginRequest, OccupiedSlot
from api.mock.database.model import model

# This method is filling a db_session with the official test data from the test_model.py file
def fill(db_session: Session):
    # Clear existing data
    db_session.query(OccupiedSlot).delete()
    db_session.query(LoginRequest).delete()
    db_session.query(Invitation).delete()
    db_session.query(Edit).delete()
    db_session.query(User).delete()
    db_session.query(Song).delete()
    db_session.query(Slot).delete()
    db_session.query(Group).delete()
    db_session.commit()
    
    # Insert groups
    groups = [Group(group_id=group.group_id, name=group.name) for group in model.groups]
    db_session.add_all(groups)
    db_session.commit()

    # Insert songs
    songs = [Song(song_id=song.song_id, name=song.name, author=song.author, times_used=song.times_used,
                  cover_src=song.cover_src, audio_src=song.audio_src) for song in model.songs]
    db_session.add_all(songs)
    db_session.commit()

    # Insert users
    users = [User(user_id=user.user_id, group_id=user.group_id, role=user.role, name=user.name, email=user.email)
             for user in model.users]
    db_session.add_all(users)
    db_session.commit()

    # Insert edits
    edits = [Edit(edit_id=edit.edit_id, song_id=edit.song_id, created_by=edit.created_by, group_id=edit.group_id,
                  name=edit.name, isLive=edit.isLive, video_src=edit.video_src) for edit in model.edits]
    db_session.add_all(edits)
    db_session.commit()

    # Insert slots (assuming you have slot data in test_model)
    slots = [Slot(slot_id=slot.slot_id, song_id=slot.song_id, start_time=slot.start_time, end_time=slot.end_time) 
             for slot in model.slots]
    db_session.add_all(slots)
    db_session.commit()

    # Insert invitations (assuming you have invitation data in test_model)
    invitations = [Invitation(invitation_id=invitation.invitation_id, group_id=invitation.group_id, token=invitation.token, 
                              email=invitation.email, created_at=invitation.created_at, expires_at=invitation.expires_at) 
                   for invitation in model.invitations]
    db_session.add_all(invitations)
    db_session.commit()

    # Insert login requests (assuming you have login request data in test_model)
    login_requests = [LoginRequest(user_id=login_request.user_id, pin=login_request.pin, 
                                   created_at=login_request.created_at, expires_at=login_request.expires_at) 
                      for login_request in model.login_requests]
    db_session.add_all(login_requests)
    db_session.commit()

    # Insert occupied slots
    occupied_slots = [OccupiedSlot(occupied_slot_id=occupied_slot.occupied_slot_id, user_id=occupied_slot.user_id, 
                                   slot_id=occupied_slot.slot_id, edit_id=occupied_slot.edit_id, 
                                   video_src=occupied_slot.video_src) 
                      for occupied_slot in model.occupied_slots]
    db_session.add_all(occupied_slots)
    db_session.commit()
