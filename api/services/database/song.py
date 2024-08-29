from typing import List, Optional
from sqlalchemy.orm import Session
from api.models.database.model import Song, Slot

def create(
        name: str, 
        author: str, 
        cover_src: str, 
        audio_src:str, 
        db_session: Session) -> Song:
    
    new_song = Song(
        name=name,
        author=author,
        times_used=0,
        cover_src=cover_src,
        audio_src=audio_src
    )
    db_session.add(new_song)
    db_session.commit()
    db_session.refresh(new_song)
    return new_song

def get(song_id: int, db_session: Session) -> Song:
    return db_session.query(Song).filter(Song.song_id == song_id).one_or_none()

def list_all(db_session: Session) -> List[Song]:
    return db_session.query(Song).all()

def update(
    song_id: int,
    name: Optional[str] = None,
    author: Optional[str] = None,
    cover_src: Optional[str] = None,
    audio_src: Optional[str] = None,
    db_session: Session = None
) -> Optional[Song]:
    # Suche nach dem Song in der Datenbank
    song = db_session.query(Song).filter(Song.song_id == song_id).one_or_none()

    # Wenn der Song nicht gefunden wird, None zurückgeben
    if not song:
        return None

    # Aktualisiere die Felder, wenn neue Werte übergeben wurden
    if name is not None:
        song.name = name
    if author is not None:
        song.author = author
    if cover_src is not None:
        song.cover_src = cover_src
    if audio_src is not None:
        song.audio_src = audio_src

    # Änderungen in der Datenbank speichern
    db_session.commit()
    db_session.refresh(song)

    return song

def remove(song_id: int, db_session: Session) -> bool:
    song = db_session.query(Song).filter(Song.song_id == song_id).first()
    if song:
        db_session.delete(song)
        db_session.commit()
        return True
    return False

def get_breakpoints(song_id: int, db_session: Session) -> List[float]:
    """
    Gibt eine Liste aller Breakpoints (Start- und Endzeiten) für die Slots eines Songs zurück.
    """
    slots = db_session.query(Slot).filter(Slot.song_id == song_id).all()
    breakpoints = set()

    # Durchlaufe alle Slots und füge die Start- und Endzeiten zu den Breakpoints hinzu
    for slot in slots:
        breakpoints.add(slot.start_time)
        breakpoints.add(slot.end_time)

    # Sortiere die Breakpoints und konvertiere sie in eine Liste
    return sorted(breakpoints)

def create_slots_from_breakpoints(song_id: int, breakpoints: List[float], db_session: Session) -> List[Slot]:
    """
    Create slots based on the provided breakpoints for the specified song.

    Args:
        song_id (int): The ID of the song for which slots are to be created.
        breakpoints (List[float]): A list of breakpoints (start and end times).
        db_session (Session): The database session to perform operations.

    Returns:
        List[Slot]: A list of newly created slots.
    """
    # Ensure the breakpoints are sorted
    breakpoints = sorted(breakpoints)
    slots = []

    # Create slots from breakpoints
    for i in range(len(breakpoints) - 1):
        slot = Slot(
            song_id=song_id,
            start_time=breakpoints[i],
            end_time=breakpoints[i + 1]
        )
        slots.append(slot)

    # Add all slots to the session and commit
    db_session.add_all(slots)
    db_session.commit()

    # Refresh the slots to get the IDs and other database-generated fields
    for slot in slots:
        db_session.refresh(slot)

    return slots
    