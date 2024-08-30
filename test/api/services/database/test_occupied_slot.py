from sqlalchemy.orm import Session
from api.models.database.model import OccupiedSlot, Slot
from api.services.database.occupied_slot import create, get, get_occupied_slots_for_edit, is_slot_occupied, remove
from api.mock.database.model import mock_model_local_links

# create
def test_create_occupied_slot(db_memory: Session):
    # Arrange
    user_id = mock_model_local_links.users[0].user_id  # Verwende eine gültige user_id aus den Testdaten
    slot_id = mock_model_local_links.slots[0].slot_id  # Verwende eine gültige slot_id aus den Testdaten
    edit_id = mock_model_local_links.edits[0].edit_id  # Verwende eine gültige edit_id aus den Testdaten
    video_src = "http://example.com/new_occupied_slot.mp4"

    # Act: Erstelle einen neuen OccupiedSlot
    new_occupied_slot = create(user_id=user_id, slot_id=slot_id, edit_id=edit_id, video_src=video_src, db=db_memory)
    
    # Assert: Überprüfe die Attribute des erstellten OccupiedSlots
    assert new_occupied_slot.user_id == user_id
    assert new_occupied_slot.slot_id == slot_id
    assert new_occupied_slot.edit_id == edit_id
    assert new_occupied_slot.video_src == video_src

    # Verify: Stelle sicher, dass der OccupiedSlot in der Datenbank gespeichert wurde
    occupied_slot_in_db = db_memory.query(OccupiedSlot).filter_by(occupied_slot_id=new_occupied_slot.occupied_slot_id).one_or_none()
    assert occupied_slot_in_db is not None
    assert occupied_slot_in_db.user_id == user_id
    assert occupied_slot_in_db.slot_id == slot_id
    assert occupied_slot_in_db.edit_id == edit_id
    assert occupied_slot_in_db.video_src == video_src

# get
def test_get_occupied_slot(db_memory: Session):
    # Arrange: Verwende einen vorhandenen OccupiedSlot aus den Testdaten
    existing_occupied_slot = mock_model_local_links.occupied_slots[0]
    
    # Act: Hole den OccupiedSlot mit seiner ID
    fetched_occupied_slot = get(existing_occupied_slot.occupied_slot_id, db_memory)
    
    # Assert: Überprüfe, ob der gefundene OccupiedSlot den erwarteten Werten entspricht
    assert fetched_occupied_slot is not None
    assert fetched_occupied_slot.occupied_slot_id == existing_occupied_slot.occupied_slot_id
    assert fetched_occupied_slot.user_id == existing_occupied_slot.user_id
    assert fetched_occupied_slot.slot_id == existing_occupied_slot.slot_id
    assert fetched_occupied_slot.edit_id == existing_occupied_slot.edit_id
    assert fetched_occupied_slot.video_src == existing_occupied_slot.video_src

def test_get_occupied_slot_failed(db_memory: Session):
    # Arrange: Verwende eine ungültige occupied_slot_id
    non_existent_occupied_slot_id = 9999
    
    # Act: Versuche, den OccupiedSlot mit der ungültigen ID abzurufen
    fetched_occupied_slot = get(non_existent_occupied_slot_id, db_memory)
    
    # Assert: Stelle sicher, dass kein OccupiedSlot gefunden wird
    assert fetched_occupied_slot is None

# remove
def test_remove_occupied_slot(db_memory: Session):
    # Arrange: Verwende einen vorhandenen Occupied Slot
    existing_occupied_slot = db_memory.query(OccupiedSlot).first()

    # Act: Lösche den Occupied Slot
    result = remove(existing_occupied_slot.occupied_slot_id, db_memory)

    # Assert: Überprüfe, dass der Occupied Slot erfolgreich gelöscht wurde
    assert result is True

    # Verify: Stelle sicher, dass der Occupied Slot nicht mehr in der Datenbank vorhanden ist
    occupied_slot_in_db = db_memory.query(OccupiedSlot).filter_by(occupied_slot_id=existing_occupied_slot.occupied_slot_id).one_or_none()
    assert occupied_slot_in_db is None

    # cascading: OccupiedSlot -> Slot
    slot_in_db = db_memory.query(Slot).filter_by(slot_id=existing_occupied_slot.slot_id).first()
    assert slot_in_db is not None  # Slot bleibt bestehen

def test_remove_occupied_slot_failed(db_memory: Session):
    # Arrange: Verwende eine ungültige occupied_slot_id
    non_existent_occupied_slot_id = 9999

    # Act: Versuche, den Occupied Slot mit der ungültigen ID zu löschen
    result = remove(non_existent_occupied_slot_id, db_memory)

    # Assert: Stelle sicher, dass kein Occupied Slot gelöscht wird
    assert result is False

#test get occupied slots for edit
def test_get_occupied_slots_for_edit(db_memory: Session):
    res = get_occupied_slots_for_edit(3, db_memory)
    assert len(res) == 6
    
def test_get_occupied_slots_for_edit_other(db_memory: Session):
    res = get_occupied_slots_for_edit(1, db_memory)
    assert len(res) == 1
    
def test_is_slot_occupied_1(db_memory: Session):
    assert is_slot_occupied(1,1, db_memory) == True
    
def test_is_slot_occupied_2(db_memory: Session):
    assert is_slot_occupied(1,2, db_memory) == False