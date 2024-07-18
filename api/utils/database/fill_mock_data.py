import random
from sqlalchemy.orm import Session
from api.models.database.model import Group, User, Song, Edit

def fill_mock_data(db_session: Session):
    # Clear existing data
    db_session.query(Edit).delete()
    db_session.query(User).delete()
    db_session.query(Song).delete()
    db_session.query(Group).delete()
    db_session.commit()
    
    # Create 3 groups
    groups = []
    for i in range(1, 4):
        group = Group(name=f"Group {i}")
        db_session.add(group)
        db_session.commit()
        db_session.refresh(group)
        groups.append(group)
    
    # Create 3 songs
    songs = []
    for i in range(1, 4):
        song = Song(
            name=f"Song {i}",
            author=f"Author {i}",
            times_used=0,
            cover_src=f"http://example.com/cover{i}.jpg",
            audio_src=f"http://example.com/audio{i}.mp3"
        )
        db_session.add(song)
        db_session.commit()
        db_session.refresh(song)
        songs.append(song)

    # Create users for each group: 1 creator and 2 members
    creators = {}
    members_by_group = {}
    for group in groups:
        creator = User(
            group_id=group.group_id,
            role="creator",
            name=f"Creator of {group.name}",
            email=f"creator{group.group_id}@example.com"
        )
        db_session.add(creator)
        db_session.commit()
        db_session.refresh(creator)
        creators[group.group_id] = creator

        members = []
        for j in range(1, 3):
            member = User(
                group_id=group.group_id,
                role="member",
                name=f"Member {j} of {group.name}",
                email=f"member{j}_{group.group_id}@example.com"
            )
            db_session.add(member)
            db_session.commit()
            db_session.refresh(member)
            members.append(member)
        
        members_by_group[group.group_id] = members

    # Create 3 edits for each group
    for group in groups:
        creator = creators[group.group_id]  # Get the creator for the current group
        members = members_by_group[group.group_id]  # Get members for the current group
        
        # Create the first edit by the creator
        first_edit = Edit(
            song_id=songs[0].song_id,
            created_by=creator.user_id,
            group_id=group.group_id,
            name=f"Edit 1 of {group.name}",
            isLive=True
        )
        db_session.add(first_edit)
        db_session.commit()
        db_session.refresh(first_edit)

        # Create subsequent edits by random members
        for i in range(2, 4):
            # Randomly select a member, excluding the creator
            random_member = random.choice(members)
            edit = Edit(
                song_id=songs[i-1].song_id,
                created_by=random_member.user_id,
                group_id=group.group_id,
                name=f"Edit {i} of {group.name}",
                isLive=True
            )
            db_session.add(edit)
            db_session.commit()
            db_session.refresh(edit)
