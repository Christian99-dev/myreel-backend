from typing import List, Optional
from sqlalchemy.orm import Session
from api.models.database.model import Song, Slot

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