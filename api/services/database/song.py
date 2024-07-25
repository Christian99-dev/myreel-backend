from typing import List
from sqlalchemy.orm import Session
from api.models.database.model import Song

def create(
        name: str, 
        author: str, 
        cover_src: str, 
        audio_src:str, 
        db: Session) -> Song:
    
    new_song = Song(
        name=name,
        author=author,
        times_used=0,
        cover_src=cover_src,
        audio_src=audio_src
    )
    db.add(new_song)
    db.commit()
    db.refresh(new_song)
    return new_song

def get(song_id: int, db_session: Session) -> Song:
    return db_session.query(Song).filter(Song.song_id == song_id).one_or_none()

def list_all(db_session: Session) -> List[Song]:
    return db_session.query(Song).all()