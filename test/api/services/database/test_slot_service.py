from sqlalchemy.orm import Session
from api.models.database.model import Slot
from api.services.database.slot import create, get
from api.mock.database.model import model

# create
def test_create_slot(db_memory: Session):
    # Arrange
    song_id = model.songs[0].song_id  # Verwende eine gültige song_id aus den Testdaten
    start_time = 10.5
    end_time = 20.0

    # Act: Erstelle einen neuen Slot
    new_slot = create(song_id=song_id, start_time=start_time, end_time=end_time, db=db_memory)
    
    # Assert: Überprüfe die Attribute des erstellten Slots
    assert new_slot.song_id == song_id
    assert new_slot.start_time == start_time
    assert new_slot.end_time == end_time

    # Verify: Stelle sicher, dass der Slot in der Datenbank gespeichert wurde
    slot_in_db = db_memory.query(Slot).filter_by(slot_id=new_slot.slot_id).one_or_none()
    assert slot_in_db is not None
    assert slot_in_db.song_id == song_id
    assert slot_in_db.start_time == start_time
    assert slot_in_db.end_time == end_time

# get
def test_get_slot(db_memory: Session):
    # Arrange: Verwende einen vorhandenen Slot aus den Testdaten
    existing_slot = model.slots[0]
    
    # Act: Hole den Slot mit seiner ID
    fetched_slot = get(existing_slot.slot_id, db_memory)
    
    # Assert: Überprüfe, ob der gefundene Slot den erwarteten Werten entspricht
    assert fetched_slot is not None
    assert fetched_slot.slot_id == existing_slot.slot_id
    assert fetched_slot.song_id == existing_slot.song_id
    assert fetched_slot.start_time == existing_slot.start_time
    assert fetched_slot.end_time == existing_slot.end_time

def test_get_slot_failed(db_memory: Session):
    # Arrange: Verwende eine ungültige slot_id
    non_existent_slot_id = 9999
    
    # Act: Versuche, den Slot mit der ungültigen ID abzurufen
    fetched_slot = get(non_existent_slot_id, db_memory)
    
    # Assert: Stelle sicher, dass kein Slot gefunden wird
    assert fetched_slot is None
