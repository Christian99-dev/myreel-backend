from sqlalchemy.orm import Session
from mock.database.model import mock_model_local_links
from api.models.database.model import Slot, OccupiedSlot
from api.services.database.slot import create, get, get_slots_for_edit, remove

# create
def test_create_slot(db_memory: Session):
    # Arrange
    song_id = mock_model_local_links.songs[0].song_id  # Verwende eine gültige song_id aus den Testdaten
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
    existing_slot = mock_model_local_links.slots[0]
    
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

#remove
def test_remove_slot(db_memory: Session):
    # Arrange: Verwende einen vorhandenen Slot
    existing_slot = db_memory.query(Slot).first()

    # Act: Lösche den Slot
    result = remove(existing_slot.slot_id, db_memory)

    # Assert: Überprüfe, dass der Slot erfolgreich gelöscht wurde
    assert result is True

    # Verify: Stelle sicher, dass der Slot nicht mehr in der Datenbank vorhanden ist
    slot_in_db = db_memory.query(Slot).filter_by(slot_id=existing_slot.slot_id).one_or_none()
    assert slot_in_db is None

    # cascading: Slot -> OccupiedSlot
    occupied_slots_in_db = db_memory.query(OccupiedSlot).filter_by(slot_id=existing_slot.slot_id).all()
    assert len(occupied_slots_in_db) == 0

def test_remove_slot_failed(db_memory: Session):
    # Arrange: Verwende eine ungültige slot_id
    non_existent_slot_id = 9999

    # Act: Versuche, den Slot mit der ungültigen ID zu löschen
    result = remove(non_existent_slot_id, db_memory)

    # Assert: Stelle sicher, dass kein Slot gelöscht wird
    assert result is False
    
# test get slots for edit
def test_get_slot_for_edit(db_memory: Session):
    res = get_slots_for_edit(3, db_memory)
    assert len(res) == 6
    
def test_get_slot_for_edit_again(db_memory: Session):
    res = get_slots_for_edit(1, db_memory)
    assert len(res) == 3