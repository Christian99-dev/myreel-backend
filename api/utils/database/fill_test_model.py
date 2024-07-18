from sqlalchemy.orm import Session
from api.models.database.model import Group, Song, User, Edit
from api.utils.database.test_model import test_model  # Importiere deine SQLAlchemy-Modelle hier entsprechend

def fill_test_model(db_session: Session):
    # Clear existing data
    db_session.query(Edit).delete()
    db_session.query(User).delete()
    db_session.query(Song).delete()
    db_session.query(Group).delete()
    db_session.commit()
    
    # Insert groups
    groups = [Group(group_id=group.group_id, name=group.name) for group in test_model.groups]
    db_session.add_all(groups)
    db_session.commit()

    # Insert songs
    songs = [Song(song_id=song.song_id, name=song.name, author=song.author, times_used=song.times_used,
                  cover_src=song.cover_src, audio_src=song.audio_src) for song in test_model.songs]
    db_session.add_all(songs)
    db_session.commit()

    # Insert users
    users = [User(user_id=user.user_id, group_id=user.group_id, role=user.role, name=user.name, email=user.email)
             for user in test_model.users]
    db_session.add_all(users)
    db_session.commit()

    # Insert edits
    edits = [Edit(edit_id=edit.edit_id, song_id=edit.song_id, created_by=edit.created_by, group_id=edit.group_id,
                  name=edit.name, isLive=edit.isLive) for edit in test_model.edits]
    db_session.add_all(edits)
    db_session.commit()
