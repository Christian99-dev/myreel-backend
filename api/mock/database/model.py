from pydantic import BaseModel
from typing import List, Optional
from api.utils.database.create_uuid import create_uuid
from datetime import datetime, timedelta

# main model tables

class Group(BaseModel):
    group_id: Optional[str]
    name: str

class Song(BaseModel):
    song_id: Optional[int]
    name: str
    author: str
    times_used: int
    cover_src: str
    audio_src: str

class User(BaseModel):
    user_id: Optional[int]
    group_id: str
    role: str
    name: str
    email: str

class Edit(BaseModel):
    edit_id: Optional[int]
    song_id: int
    created_by: int
    group_id: str
    name: str
    isLive: bool
    video_src: str

class Slot(BaseModel):
    slot_id: Optional[int]
    song_id: int
    start_time: float
    end_time: float

class Invitation(BaseModel):
    invitation_id: Optional[int]
    group_id: str
    token: str
    email: str
    created_at: datetime
    expires_at: datetime

class LoginRequest(BaseModel):
    user_id: int
    pin: str
    created_at: datetime
    expires_at: datetime

class OccupiedSlot(BaseModel):
    occupied_slot_id: Optional[int]
    user_id: int
    slot_id: int
    edit_id: int
    video_src: str

# main model
class Model(BaseModel):
    groups: List[Group]
    songs: List[Song]
    users: List[User]
    edits: List[Edit]
    slots: List[Slot]
    invitations: List[Invitation]
    login_requests: List[LoginRequest]
    occupied_slots: List[OccupiedSlot]

group_id_1 = create_uuid()
group_id_2 = create_uuid()
group_id_3 = create_uuid()

now = datetime.utcnow()

mock_model_local_links = Model(
    groups=[
        Group(group_id=group_id_1, name="Group 1"),
        Group(group_id=group_id_2, name="Group 2"),
        Group(group_id=group_id_3, name="Group 3")
    ],
    songs=[
        Song(song_id=1, name="Song 1", author="Author 1", times_used=0, cover_src="http://localhost:8000/static/covers/1.png", audio_src="http://localhost:8000/static/songs/1.wav"),
        Song(song_id=2, name="Song 2", author="Author 2", times_used=0, cover_src="http://localhost:8000/static/covers/2.png", audio_src="http://localhost:8000/static/songs/2.wav"),
        Song(song_id=3, name="Song 3", author="Author 3", times_used=0, cover_src="http://localhost:8000/static/covers/3.png", audio_src="http://localhost:8000/static/songs/3.wav")
    ],
    users=[
        User(user_id=1, group_id=group_id_1, role="creator", name="Creator of Group 1", email="creator1@example.com"),
        User(user_id=2, group_id=group_id_1, role="member", name="Member 1 of Group 1", email="member1_1@example.com"),
        User(user_id=3, group_id=group_id_1, role="member", name="Member 2 of Group 1", email="member2_1@example.com"),
        User(user_id=4, group_id=group_id_2, role="creator", name="Creator of Group 2", email="creator2@example.com"),
        User(user_id=5, group_id=group_id_2, role="member", name="Member 1 of Group 2", email="member1_2@example.com"),
        User(user_id=6, group_id=group_id_2, role="member", name="Member 2 of Group 2", email="member2_2@example.com"),
        User(user_id=7, group_id=group_id_3, role="creator", name="Creator of Group 3", email="creator3@example.com"),
        User(user_id=8, group_id=group_id_3, role="member", name="Member 1 of Group 3", email="member1_3@example.com"),
        User(user_id=9, group_id=group_id_3, role="member", name="Member 2 of Group 3", email="member2_3@example.com")
    ],
    edits=[
        Edit(edit_id=1, song_id=1, created_by=1, group_id=group_id_1, name="Edit 1 of Group 1", isLive=False, video_src="http://localhost:8000/static/edits/1.mp4"),
        Edit(edit_id=2, song_id=2, created_by=3, group_id=group_id_1, name="Edit 2 of Group 1", isLive=False, video_src="http://localhost:8000/static/edits/2.mp4"),
        Edit(edit_id=3, song_id=3, created_by=2, group_id=group_id_1, name="Edit 3 of Group 1", isLive=False, video_src="http://localhost:8000/static/edits/3.mp4"),
        Edit(edit_id=4, song_id=1, created_by=4, group_id=group_id_2, name="Edit 1 of Group 2", isLive=False, video_src="http://localhost:8000/static/edits/4.mp4"),
        Edit(edit_id=5, song_id=2, created_by=6, group_id=group_id_2, name="Edit 2 of Group 2", isLive=False, video_src="http://localhost:8000/static/edits/5.mp4"),
        Edit(edit_id=6, song_id=3, created_by=6, group_id=group_id_2, name="Edit 3 of Group 2", isLive=False, video_src="http://localhost:8000/static/edits/6.mp4"),
        Edit(edit_id=7, song_id=1, created_by=7, group_id=group_id_3, name="Edit 1 of Group 3", isLive=False, video_src="http://localhost:8000/static/edits/7.mp4"),
        Edit(edit_id=8, song_id=2, created_by=9, group_id=group_id_3, name="Edit 2 of Group 3", isLive=False, video_src="http://localhost:8000/static/edits/8.mp4"),
        Edit(edit_id=9, song_id=3, created_by=8, group_id=group_id_3, name="Edit 3 of Group 3", isLive=False, video_src="http://localhost:8000/static/edits/9.mp4")
    ],
    slots=[
        Slot(slot_id=1, song_id=1, start_time=0,   end_time=0.5),
        Slot(slot_id=2, song_id=1, start_time=1,   end_time=1.5),
        Slot(slot_id=3, song_id=1, start_time=2,   end_time=2.5),
        
        Slot(slot_id=4, song_id=2, start_time=0,   end_time=0.5),
        Slot(slot_id=5, song_id=2, start_time=1,   end_time=1.5),
        Slot(slot_id=6, song_id=2, start_time=2,   end_time=2.5),
        
        Slot(slot_id=7, song_id=3, start_time=0,   end_time=0.5),
        Slot(slot_id=8, song_id=3, start_time=1,   end_time=1.5),
        Slot(slot_id=9, song_id=3, start_time=2,   end_time=2.5)
    ],
    invitations=[
        Invitation(invitation_id=1, group_id=group_id_1, token="token1", email="invitee1@example.com", created_at=now, expires_at=now + timedelta(days=1)),
        Invitation(invitation_id=2, group_id=group_id_2, token="token2", email="invitee2@example.com", created_at=now, expires_at=now + timedelta(days=1)),
        Invitation(invitation_id=3, group_id=group_id_3, token="token3", email="invitee3@example.com", created_at=now, expires_at=now + timedelta(days=1))
    ],
    login_requests=[
        LoginRequest(user_id=1, pin="1234", created_at=now, expires_at=now + timedelta(minutes=10)),
        LoginRequest(user_id=2, pin="5678", created_at=now, expires_at=now + timedelta(minutes=10)),
        LoginRequest(user_id=3, pin="91011", created_at=now, expires_at=now + timedelta(minutes=10))
    ],
    occupied_slots=[
        OccupiedSlot(occupied_slot_id=1, user_id=1, slot_id=1, edit_id=1, video_src="http://localhost:8000/static/slots/1.mp4"),
        OccupiedSlot(occupied_slot_id=2, user_id=2, slot_id=2, edit_id=2, video_src="http://localhost:8000/static/slots/2.mp4"),
        OccupiedSlot(occupied_slot_id=3, user_id=3, slot_id=3, edit_id=3, video_src="http://localhost:8000/static/slots/3.mp4")
    ]
)

mock_model_memory_links = Model(
    groups=[
        Group(group_id=group_id_1, name="Group 1"),
        Group(group_id=group_id_2, name="Group 2"),
        Group(group_id=group_id_3, name="Group 3")
    ],
    songs=[
        Song(song_id=1, name="Song 1", author="Author 1", times_used=0, cover_src="memory://covers/1.png", audio_src="memory://songs/1.wav"),
        Song(song_id=2, name="Song 2", author="Author 2", times_used=0, cover_src="memory://covers/2.png", audio_src="memory://songs/2.wav"),
        Song(song_id=3, name="Song 3", author="Author 3", times_used=0, cover_src="memory://covers/3.png", audio_src="memory://songs/3.wav")
    ],
    users=[
        User(user_id=1, group_id=group_id_1, role="creator", name="Creator of Group 1", email="creator1@example.com"),
        User(user_id=2, group_id=group_id_1, role="member", name="Member 1 of Group 1", email="member1_1@example.com"),
        User(user_id=3, group_id=group_id_1, role="member", name="Member 2 of Group 1", email="member2_1@example.com"),
        User(user_id=4, group_id=group_id_2, role="creator", name="Creator of Group 2", email="creator2@example.com"),
        User(user_id=5, group_id=group_id_2, role="member", name="Member 1 of Group 2", email="member1_2@example.com"),
        User(user_id=6, group_id=group_id_2, role="member", name="Member 2 of Group 2", email="member2_2@example.com"),
        User(user_id=7, group_id=group_id_3, role="creator", name="Creator of Group 3", email="creator3@example.com"),
        User(user_id=8, group_id=group_id_3, role="member", name="Member 1 of Group 3", email="member1_3@example.com"),
        User(user_id=9, group_id=group_id_3, role="member", name="Member 2 of Group 3", email="member2_3@example.com")
    ],
    edits=[
        Edit(edit_id=1, song_id=1, created_by=1, group_id=group_id_1, name="Edit 1 of Group 1", isLive=False, video_src="memory://edits/1.mp4"),
        Edit(edit_id=2, song_id=2, created_by=3, group_id=group_id_1, name="Edit 2 of Group 1", isLive=False, video_src="memory://edits/2.mp4"),
        Edit(edit_id=3, song_id=3, created_by=2, group_id=group_id_1, name="Edit 3 of Group 1", isLive=False, video_src="memory://edits/3.mp4"),
        Edit(edit_id=4, song_id=1, created_by=4, group_id=group_id_2, name="Edit 1 of Group 2", isLive=False, video_src="memory://edits/4.mp4"),
        Edit(edit_id=5, song_id=2, created_by=6, group_id=group_id_2, name="Edit 2 of Group 2", isLive=False, video_src="memory://edits/5.mp4"),
        Edit(edit_id=6, song_id=3, created_by=6, group_id=group_id_2, name="Edit 3 of Group 2", isLive=False, video_src="memory://edits/6.mp4"),
        Edit(edit_id=7, song_id=1, created_by=7, group_id=group_id_3, name="Edit 1 of Group 3", isLive=False, video_src="memory://edits/7.mp4"),
        Edit(edit_id=8, song_id=2, created_by=9, group_id=group_id_3, name="Edit 2 of Group 3", isLive=False, video_src="memory://edits/8.mp4"),
        Edit(edit_id=9, song_id=3, created_by=8, group_id=group_id_3, name="Edit 3 of Group 3", isLive=False, video_src="memory://edits/9.mp4")
    ],
    slots=[
        Slot(slot_id=1, song_id=1, start_time=0,   end_time=0.5),
        Slot(slot_id=2, song_id=1, start_time=1,   end_time=1.5),
        Slot(slot_id=3, song_id=1, start_time=2,   end_time=2.5),
        
        Slot(slot_id=4, song_id=2, start_time=0,   end_time=0.5),
        Slot(slot_id=5, song_id=2, start_time=1,   end_time=1.5),
        Slot(slot_id=6, song_id=2, start_time=2,   end_time=2.5),
        
        Slot(slot_id=7, song_id=3, start_time=0,   end_time=0.5),
        Slot(slot_id=8, song_id=3, start_time=1,   end_time=1.5),
        Slot(slot_id=9, song_id=3, start_time=2,   end_time=2.5)
    ],
    invitations=[
        Invitation(invitation_id=1, group_id=group_id_1, token="token1", email="invitee1@example.com", created_at=now, expires_at=now + timedelta(days=1)),
        Invitation(invitation_id=2, group_id=group_id_2, token="token2", email="invitee2@example.com", created_at=now, expires_at=now + timedelta(days=1)),
        Invitation(invitation_id=3, group_id=group_id_3, token="token3", email="invitee3@example.com", created_at=now, expires_at=now + timedelta(days=1))
    ],
    login_requests=[
        LoginRequest(user_id=1, pin="1234", created_at=now, expires_at=now + timedelta(minutes=10)),
        LoginRequest(user_id=2, pin="5678", created_at=now, expires_at=now + timedelta(minutes=10)),
        LoginRequest(user_id=3, pin="91011", created_at=now, expires_at=now + timedelta(minutes=10))
    ],
    occupied_slots=[
        OccupiedSlot(occupied_slot_id=1, user_id=1, slot_id=1, edit_id=1, video_src="memory://slots/1.mp4"),
        OccupiedSlot(occupied_slot_id=2, user_id=2, slot_id=2, edit_id=2, video_src="memory://slots/2.mp4"),
        OccupiedSlot(occupied_slot_id=3, user_id=3, slot_id=3, edit_id=3, video_src="memory://slots/3.mp4")
    ]
)