from typing import List, Optional

from sqlalchemy.exc import NoResultFound
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
    song = database_session.query(Song).filter(Song.song_id == song_id).one_or_none()
    if not song:
        raise NoResultFound(f"Song with ID {song_id} not found.")
    return song

def update(song_id: int, name: Optional[str] = None, author: Optional[str] = None, cover_src: Optional[str] = None, audio_src: Optional[str] = None, database_session: Session = None) -> Song:
    song = database_session.query(Song).filter(Song.song_id == song_id).one_or_none()
    if not song:
        raise NoResultFound(f"Song with ID {song_id} not found.")
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

def remove(song_id: int, database_session: Session) -> None:
    song = database_session.query(Song).filter(Song.song_id == song_id).one_or_none()
    if not song:
        raise NoResultFound(f"Song with ID {song_id} not found.")
    database_session.delete(song)
    database_session.commit()

"""Andere Operationen"""

def list_all(database_session: Session) -> List[Song]:
    """
    Gibt alle Songs zurück.
    Wenn keine Songs vorhanden sind, wird eine NoResultFound Exception geworfen.
    """
    songs = database_session.query(Song).all()
    if not songs:
        raise NoResultFound("No songs found in the database.")
    return songs

def get_breakpoints(song_id: int, database_session: Session) -> List[float]:
    """
    Gibt die Start- und Endzeiten (Breakpoints) für alle Slots eines bestimmten Songs zurück.
    Wenn keine Slots für den Song existieren, wird eine NoResultFound Exception geworfen.
    """
    slots = database_session.query(Slot).filter(Slot.song_id == song_id).all()
    if not slots:
        raise NoResultFound(f"No slots found for song ID {song_id}")
    
    breakpoints = set()
    for slot in slots:
        breakpoints.add(slot.start_time)
        breakpoints.add(slot.end_time)
    return sorted(breakpoints)

def create_slots_from_breakpoints(song_id: int, breakpoints: List[float], database_session: Session) -> List[Slot]:
    """
    Erstellt Slots basierend auf einer Liste von Breakpoints. Es werden Slots zwischen benachbarten Breakpoints erstellt.
    Wenn die Breakpoint-Liste leer oder zu klein ist, wird eine Exception geworfen.
    """
    if len(breakpoints) < 2:
        raise ValueError("At least two breakpoints are required to create slots.")
    
    breakpoints = sorted(breakpoints)
    slots = []
    for i in range(len(breakpoints) - 1):
        slot = Slot(song_id=song_id, start_time=breakpoints[i], end_time=breakpoints[i + 1])
        slots.append(slot)
    
    if not slots:
        raise ValueError(f"Failed to create slots for song ID {song_id}. No valid slots could be created.")
    
    database_session.add_all(slots)
    database_session.commit()
    for slot in slots:
        database_session.refresh(slot)
    return slots
