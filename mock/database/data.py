from datetime import datetime, timedelta

data = {
    "groups": [
        {"group_id": "11111111-1111-1111-1111-111111111111", "name": "Group 1"},
        {"group_id": "22222222-2222-2222-2222-222222222222", "name": "Group 2"},
        {"group_id": "33333333-3333-3333-3333-333333333333", "name": "Group 3"}
    ],
    "songs": [
        {"song_id": 1, "name": "Song 1", "author": "Author 1", "times_used": 0, "cover_src": "http://localhost:8000/files/covers/1.png", "audio_src": "http://localhost:8000/files/songs/1.wav"},
        {"song_id": 2, "name": "Song 2", "author": "Author 2", "times_used": 0, "cover_src": "http://localhost:8000/files/covers/2.png", "audio_src": "http://localhost:8000/files/songs/2.wav"},
        {"song_id": 3, "name": "Song 3", "author": "Author 3", "times_used": 0, "cover_src": "http://localhost:8000/files/covers/3.png", "audio_src": "http://localhost:8000/files/songs/3.wav"}
    ],
    "users": [
        {"user_id": 1, "group_id": "11111111-1111-1111-1111-111111111111", "role": "creator", "name": "Creator of Group 1", "email": "creator1@example.com"},
        {"user_id": 2, "group_id": "11111111-1111-1111-1111-111111111111", "role": "member", "name": "Member 1 of Group 1", "email": "member1_1@example.com"},
        {"user_id": 3, "group_id": "11111111-1111-1111-1111-111111111111", "role": "member", "name": "Member 2 of Group 1", "email": "member2_1@example.com"},
        {"user_id": 4, "group_id": "22222222-2222-2222-2222-222222222222", "role": "creator", "name": "Creator of Group 2", "email": "creator2@example.com"},
        {"user_id": 5, "group_id": "22222222-2222-2222-2222-222222222222", "role": "member", "name": "Member 1 of Group 2", "email": "member1_2@example.com"},
        {"user_id": 6, "group_id": "22222222-2222-2222-2222-222222222222", "role": "member", "name": "Member 2 of Group 2", "email": "member2_2@example.com"},
        {"user_id": 7, "group_id": "33333333-3333-3333-3333-333333333333", "role": "creator", "name": "Creator of Group 3", "email": "creator3@example.com"},
        {"user_id": 8, "group_id": "33333333-3333-3333-3333-333333333333", "role": "member", "name": "Member 1 of Group 3", "email": "member1_3@example.com"},
        {"user_id": 9, "group_id": "33333333-3333-3333-3333-333333333333", "role": "member", "name": "Member 2 of Group 3", "email": "member2_3@example.com"}
    ],
    "edits": [
        {"edit_id": 1, "song_id": 1, "created_by": 1, "group_id": "11111111-1111-1111-1111-111111111111", "name": "Edit 1 of Group 1", "isLive": False, "video_src": "http://localhost:8000/files/edits/1.mp4"},
        {"edit_id": 2, "song_id": 2, "created_by": 3, "group_id": "11111111-1111-1111-1111-111111111111", "name": "Edit 2 of Group 1", "isLive": False, "video_src": "http://localhost:8000/files/edits/2.mp4"},
        {"edit_id": 3, "song_id": 3, "created_by": 2, "group_id": "11111111-1111-1111-1111-111111111111", "name": "Edit 3 of Group 1", "isLive": False, "video_src": "http://localhost:8000/files/edits/3.mp4"},
        {"edit_id": 4, "song_id": 1, "created_by": 4, "group_id": "22222222-2222-2222-2222-222222222222", "name": "Edit 1 of Group 2", "isLive": False, "video_src": "http://localhost:8000/files/edits/4.mp4"},
        {"edit_id": 5, "song_id": 2, "created_by": 6, "group_id": "22222222-2222-2222-2222-222222222222", "name": "Edit 2 of Group 2", "isLive": False, "video_src": "http://localhost:8000/files/edits/5.mp4"},
        {"edit_id": 6, "song_id": 3, "created_by": 6, "group_id": "22222222-2222-2222-2222-222222222222", "name": "Edit 3 of Group 2", "isLive": False, "video_src": "http://localhost:8000/files/edits/6.mp4"},
        {"edit_id": 7, "song_id": 1, "created_by": 7, "group_id": "33333333-3333-3333-3333-333333333333", "name": "Edit 1 of Group 3", "isLive": False, "video_src": "http://localhost:8000/files/edits/7.mp4"},
        {"edit_id": 8, "song_id": 2, "created_by": 9, "group_id": "33333333-3333-3333-3333-333333333333", "name": "Edit 2 of Group 3", "isLive": False, "video_src": "http://localhost:8000/files/edits/8.mp4"},
        {"edit_id": 9, "song_id": 3, "created_by": 8, "group_id": "33333333-3333-3333-3333-333333333333", "name": "Edit 3 of Group 3", "isLive": False, "video_src": "http://localhost:8000/files/edits/9.mp4"}
    ],
    "slots": [
        {"slot_id": 1, "song_id": 1, "start_time": 0, "end_time": 0.5},
        {"slot_id": 2, "song_id": 1, "start_time": 0.5, "end_time": 1},
        {"slot_id": 3, "song_id": 1, "start_time": 1, "end_time": 2},
        {"slot_id": 4, "song_id": 2, "start_time": 0, "end_time": 0.5},
        {"slot_id": 5, "song_id": 2, "start_time": 0.5, "end_time": 1.5},
        {"slot_id": 6, "song_id": 2, "start_time": 1.5, "end_time": 3},
        {"slot_id": 7, "song_id": 3, "start_time": 0.5, "end_time": 1},
        {"slot_id": 8, "song_id": 3, "start_time": 1, "end_time": 2},
        {"slot_id": 9, "song_id": 3, "start_time": 2, "end_time": 3.1},
        {"slot_id": 10, "song_id": 3, "start_time": 3.1, "end_time": 3.3},
        {"slot_id": 11, "song_id": 3, "start_time": 3.3, "end_time": 3.6},
        {"slot_id": 12, "song_id": 3, "start_time": 3.6, "end_time": 3.8}
    ],
    "invitations": [
        {"invitation_id": 1, "group_id": "11111111-1111-1111-1111-111111111111", "token": "token1", "email": "invitee1@example.com", "created_at": datetime.now(), "expires_at": datetime.now() + timedelta(days=1)},
        {"invitation_id": 2, "group_id": "22222222-2222-2222-2222-222222222222", "token": "token2", "email": "invitee2@example.com", "created_at": datetime.now(), "expires_at": datetime.now() + timedelta(days=1)},
        {"invitation_id": 3, "group_id": "33333333-3333-3333-3333-333333333333", "token": "token3", "email": "invitee3@example.com", "created_at": datetime.now(), "expires_at": datetime.now() + timedelta(days=1)}
    ],
    "login_requests": [
        {"user_id": 1, "pin": "1234", "created_at": datetime.now(), "expires_at": datetime.now() + timedelta(minutes=10)},
        {"user_id": 2, "pin": "5678", "created_at": datetime.now(), "expires_at": datetime.now() + timedelta(minutes=10)},
        {"user_id": 3, "pin": "91011", "created_at": datetime.now(), "expires_at": datetime.now() + timedelta(minutes=10)}
    ],
    "occupied_slots": [
        {"occupied_slot_id": 1, "user_id": 1, "slot_id": 1, "edit_id": 1, "video_src": "http://localhost:8000/files/occupied_slots/1.mp4", "start_time": 0, "end_time": 0.5},
        {"occupied_slot_id": 2, "user_id": 2, "slot_id": 2, "edit_id": 2, "video_src": "http://localhost:8000/files/occupied_slots/2.mp4", "start_time": 0, "end_time": 0.5},
        {"occupied_slot_id": 3, "user_id": 3, "slot_id": 7, "edit_id": 3, "video_src": "http://localhost:8000/files/occupied_slots/3.mp4", "start_time": 0, "end_time": 0.5},
        {"occupied_slot_id": 4, "user_id": 2, "slot_id": 8, "edit_id": 3, "video_src": "http://localhost:8000/files/occupied_slots/4.mp4", "start_time": 0, "end_time": 0.5},
        {"occupied_slot_id": 5, "user_id": 1, "slot_id": 9, "edit_id": 3, "video_src": "http://localhost:8000/files/occupied_slots/5.mp4", "start_time": 0, "end_time": 0.5},
        {"occupied_slot_id": 6, "user_id": 2, "slot_id": 10, "edit_id": 3, "video_src": "http://localhost:8000/files/occupied_slots/6.mp4", "start_time": 0, "end_time": 0.5},
        {"occupied_slot_id": 7, "user_id": 3, "slot_id": 11, "edit_id": 3, "video_src": "http://localhost:8000/files/occupied_slots/7.mp4", "start_time": 0, "end_time": 0.5},
        {"occupied_slot_id": 8, "user_id": 3, "slot_id": 12, "edit_id": 3, "video_src": "http://localhost:8000/files/occupied_slots/8.mp4", "start_time": 0, "end_time": 0.5}
    ]
}