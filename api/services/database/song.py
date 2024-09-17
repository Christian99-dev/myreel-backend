from typing import List, Optional

from sqlalchemy.orm import Session

from api.models.database.model import Slot, Song

"""CRUD Operationen"""

def create(name: str, author: str, cover_src: str, audio_src: str, database_session: Session) -> Song:
    new_song = Song(
        name=name,
        author=author,
        times_used=0,
        cover_src=cover_src,
        audio_src=audio_src
    )
    database_session.add(new_song)
    database_session.commit()
    database_session.refresh(new_song)
    return new_song

def get(song_id: int, database_session: Session) -> Song:
    return database_session.query(Song).filter(Song.song_id == song_id).one_or_none()

def update(song_id: int, name: Optional[str] = None, author: Optional[str] = None, cover_src: Optional[str] = None, audio_src: Optional[str] = None, database_session: Session = None) -> Optional[Song]:
    song = database_session.query(Song).filter(Song.song_id == song_id).one_or_none()
    if not song:
        return None
    if name is not None:
        song.name = name
    if author is not None:
        song.author = author
    if cover_src is not None:
        song.cover_src = cover_src
    if audio_src is not None:
        song.audio_src = audio_src
    database_session.commit()
    database_session.refresh(song)
    return song

def remove(song_id: int, database_session: Session) -> bool:
    song = database_session.query(Song).filter(Song.song_id == song_id).first()
    if song:
        database_session.delete(song)
        database_session.commit()
        return True
    return False

"""Andere Operationen"""

def list_all(database_session: Session) -> List[Song]:
    return database_session.query(Song).all()

def get_breakpoints(song_id: int, database_session: Session) -> List[float]:
    slots = database_session.query(Slot).filter(Slot.song_id == song_id).all()
    breakpoints = set()
    for slot in slots:
        breakpoints.add(slot.start_time)
        breakpoints.add(slot.end_time)
    return sorted(breakpoints)

def create_slots_from_breakpoints(song_id: int, breakpoints: List[float], database_session: Session) -> List[Slot]:
    breakpoints = sorted(breakpoints)
    slots = []
    for i in range(len(breakpoints) - 1):
        slot = Slot(song_id=song_id, start_time=breakpoints[i], end_time=breakpoints[i + 1])
        slots.append(slot)
    database_session.add_all(slots)
    database_session.commit()
    for slot in slots:
        database_session.refresh(slot)
    return slots
