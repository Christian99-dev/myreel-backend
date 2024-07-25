from pydantic import BaseModel
from typing import List, Optional
from api.utils.database.create_uuid import create_uuid

# main model tabels
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


# main model
class Model(BaseModel):
    groups: List[Group]
    songs: List[Song]
    users: List[User]
    edits: List[Edit]

group_id_1 = create_uuid()
group_id_2 = create_uuid()
group_id_3 = create_uuid()

test_model = Model(
    groups=[
        Group(group_id=group_id_1, name="Group 1"),
        Group(group_id=group_id_2, name="Group 2"),
        Group(group_id=group_id_3, name="Group 3")
    ],
    songs=[
        Song(song_id=1, name="Song 1", author="Author 1", times_used=0, cover_src="http://example.com/cover1.jpg", audio_src="http://example.com/audio1.mp3"),
        Song(song_id=2, name="Song 2", author="Author 2", times_used=0, cover_src="http://example.com/cover2.jpg", audio_src="http://example.com/audio2.mp3"),
        Song(song_id=3, name="Song 3", author="Author 3", times_used=0, cover_src="http://example.com/cover3.jpg", audio_src="http://example.com/audio3.mp3")
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
        Edit(edit_id=1, song_id=1, created_by=1, group_id=group_id_1, name="Edit 1 of Group 1", isLive=False, video_src="http://example.com/video.mp4"),
        Edit(edit_id=2, song_id=2, created_by=3, group_id=group_id_1, name="Edit 2 of Group 1", isLive=False, video_src="http://example.com/video.mp4"),
        Edit(edit_id=3, song_id=3, created_by=2, group_id=group_id_1, name="Edit 3 of Group 1", isLive=False, video_src="http://example.com/video.mp4"),
        Edit(edit_id=4, song_id=1, created_by=4, group_id=group_id_2, name="Edit 1 of Group 2", isLive=False, video_src="http://example.com/video.mp4"),
        Edit(edit_id=5, song_id=2, created_by=6, group_id=group_id_2, name="Edit 2 of Group 2", isLive=False, video_src="http://example.com/video.mp4"),
        Edit(edit_id=6, song_id=3, created_by=6, group_id=group_id_2, name="Edit 3 of Group 2", isLive=False, video_src="http://example.com/video.mp4"),
        Edit(edit_id=7, song_id=1, created_by=7, group_id=group_id_3, name="Edit 1 of Group 3", isLive=False, video_src="http://example.com/video.mp4"),
        Edit(edit_id=8, song_id=2, created_by=9, group_id=group_id_3, name="Edit 2 of Group 3", isLive=False, video_src="http://example.com/video.mp4"),
        Edit(edit_id=9, song_id=3, created_by=8, group_id=group_id_3, name="Edit 3 of Group 3", isLive=False, video_src="http://example.com/video.mp4")
    ]
)