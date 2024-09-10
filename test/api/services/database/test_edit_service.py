from sqlalchemy.orm import Session
from api.models.database.model import Edit, OccupiedSlot, Slot
from api.services.database.edit import are_all_slots_occupied, create, get, get_edits_by_group, is_edit_creator, remove, set_is_live, update
from mock.database.data import data


# create
def test_create(memory_database_session: Session):
    # Arrange: Verwende vorhandene Testdaten
    song_id = 1  # Existiert in der gefüllten Datenbank
    created_by = 1  # Existiert in der gefüllten Datenbank
    group_id = "11111111-1111-1111-1111-111111111111"  # Verwende eine gültige group_id aus den Testdaten
    name = "New Test Edit"
    is_live = True
    video_src = "http://example.com/new_edit.mp4"

    # Act: Erstelle einen neuen Edit
    new_edit = create(song_id=song_id, created_by=created_by, group_id=group_id, name=name, is_live=is_live, video_src=video_src, database_session=memory_database_session)
    
    # Assert: Prüfe die Attribute des erstellten Edits
    assert new_edit.song_id == song_id
    assert new_edit.created_by == created_by
    assert new_edit.group_id == group_id
    assert new_edit.name == name
    assert new_edit.isLive == is_live
    assert new_edit.video_src == video_src

    # Verify: Stelle sicher, dass der Edit in der Datenbank gespeichert wurde
    edit_in_database_session = memory_database_session.query(Edit).filter_by(edit_id=new_edit.edit_id).one_or_none()
    assert edit_in_database_session is not None
    assert edit_in_database_session.song_id == song_id
    assert edit_in_database_session.created_by == created_by
    assert edit_in_database_session.group_id == group_id
    assert edit_in_database_session.name == name
    assert edit_in_database_session.isLive == is_live
    assert edit_in_database_session.video_src == video_src

# get    
def test_get(memory_database_session: Session):
    # Verwende einen vorhandenen Edit aus den Testdaten
    existing_edit = data["edits"][0]
    
    # Act: Hole den Edit mit seiner ID
    fetched_edit = get(existing_edit["edit_id"], memory_database_session)
    
    # Assert: Prüfe, ob der gefundene Edit den erwarteten Werten entspricht
    assert fetched_edit is not None
    assert fetched_edit.edit_id == existing_edit["edit_id"]
    assert fetched_edit.song_id == existing_edit["song_id"]
    assert fetched_edit.created_by == existing_edit["created_by"]
    assert fetched_edit.group_id == existing_edit["group_id"]
    assert fetched_edit.name == existing_edit["name"]
    assert fetched_edit.isLive == existing_edit["isLive"]
    assert fetched_edit.video_src == existing_edit["video_src"]

def test_get_edit_failed(memory_database_session: Session):
    # Arrange: Verwende eine ungültige edit_id
    non_existent_edit_id = 9999
    
    # Act: Versuche, den Edit mit der ungültigen ID abzurufen
    fetched_edit = get(non_existent_edit_id, memory_database_session)
    
    # Assert: Stelle sicher, dass kein Edit gefunden wird
    assert fetched_edit is None

# is_edit_creator
def test_is_edit_creator_true(memory_database_session: Session):
    # Verwende die Datenbank mit bestehenden Daten und prüfe den Ersteller eines Edits
    edit = data["edits"][0]  # Zum Beispiel: Edit 1 wurde von User 1 erstellt
    assert is_edit_creator(edit["created_by"], edit["edit_id"], memory_database_session) == True

def test_is_edit_creator_false(memory_database_session: Session):
    # Prüfe einen Fall, bei dem der User nicht der Ersteller des Edits ist
    edit = data["edits"][1]  # Zum Beispiel: Edit 2 wurde nicht von User 1 erstellt
    assert is_edit_creator(1, edit["edit_id"], memory_database_session) == False
    
# remove
def test_remove_edit(memory_database_session: Session):
    # Arrange: Verwende einen vorhandenen Edit
    existing_edit = memory_database_session.query(Edit).first()

    # Act: Lösche den Edit
    result = remove(existing_edit.edit_id, memory_database_session)

    # Assert: Überprüfe, dass der Edit erfolgreich gelöscht wurde
    assert result is True

    # Verify: Stelle sicher, dass der Edit nicht mehr in der Datenbank vorhanden ist
    edit_in_database_session = memory_database_session.query(Edit).filter_by(edit_id=existing_edit.edit_id).one_or_none()
    assert edit_in_database_session is None

    # cascading: Edit -> OccupiedSlot
    occupied_slots_in_database_session = memory_database_session.query(OccupiedSlot).filter_by(edit_id=existing_edit.edit_id).all()
    assert len(occupied_slots_in_database_session) == 0

def test_remove_edit_failed(memory_database_session: Session):
    # Arrange: Verwende eine ungültige edit_id
    non_existent_edit_id = 9999

    # Act: Versuche, den Edit mit der ungültigen ID zu löschen
    result = remove(non_existent_edit_id, memory_database_session)

    # Assert: Stelle sicher, dass kein Edit gelöscht wird
    assert result is False

# all slots are occupied    
def test_are_all_slots_occupied_true(memory_database_session: Session):
    # Arrange: Verwende einen Edit, bei dem alle Slots belegt sind
    edit_id = 3  # Beispiel: Edit 1 hat alle Slots belegt

    # Act: Überprüfe, ob alle Slots belegt sind
    result = are_all_slots_occupied(edit_id, memory_database_session)

    # Assert: Stelle sicher, dass das Ergebnis True ist
    assert result == True

def test_are_all_slots_occupied_false(memory_database_session: Session):
    # Arrange: Verwende einen Edit, bei dem nicht alle Slots belegt sind
    edit_id = 2  # Beispiel: Edit 2 hat nicht alle Slots belegt

    # Act: Überprüfe, ob alle Slots belegt sind
    result = are_all_slots_occupied(edit_id, memory_database_session)

    # Assert: Stelle sicher, dass das Ergebnis False ist
    assert result == False

def test_are_all_slots_occupied_non_existent_edit(memory_database_session: Session):
    # Arrange: Verwende eine ungültige edit_id
    non_existent_edit_id = 9999

    # Act: Überprüfe, ob alle Slots belegt sind
    result = are_all_slots_occupied(non_existent_edit_id, memory_database_session)

    # Assert: Stelle sicher, dass das Ergebnis False ist, da der Edit nicht existiert
    assert result == False

def test_set_edit_is_live_go_live(memory_database_session: Session):
        # Arrange: Fetch Edit 3 from the database
    edit = memory_database_session.query(Edit).filter_by(edit_id=3).one_or_none()
    
    assert edit is not None, "Edit 3 not found"

    # Act: Check if all slots for this edit are occupied
    if are_all_slots_occupied(edit.edit_id, memory_database_session):
        # Attempt to set the edit to live
        result = set_is_live(edit.edit_id, memory_database_session)
        
        # Assert: Check that the edit was set to live successfully
        assert result is True
        
        # Verify: Ensure that the edit's isLive status is now True
        updated_edit = memory_database_session.query(Edit).filter_by(edit_id=edit.edit_id).one()
        assert updated_edit.isLive is True
    else:
        assert False, f"Not all slots are occupied for Edit {edit.edit_id}. Cannot set it to live."

def test_set_edit_is_live_go_live(memory_database_session: Session):
        # Arrange: Fetch Edit 3 from the database
    edit = memory_database_session.query(Edit).filter_by(edit_id=2).one_or_none()
    
    assert edit is not None, "Edit 3 not found"
    assert set_is_live(edit.edit_id, memory_database_session) is False

# update edit
def test_update_name(memory_database_session: Session):
    # Arrange: Use an existing Edit
    edit = data["edits"][0]
    new_name = "Updated Edit Name"
    
    # Act: Update the name of the Edit
    updated_edit = update(edit_id=edit["edit_id"], name=new_name, database_session=memory_database_session)
    
    # Assert: Check if the name was updated
    assert updated_edit is not None
    assert updated_edit.name == new_name
    
    # Verify: Ensure that the change was committed to the database
    edit_in_database_session = memory_database_session.query(Edit).filter_by(edit_id=edit["edit_id"]).one_or_none()
    assert edit_in_database_session is not None
    assert edit_in_database_session.name == new_name
    
def test_update_non_existent_edit(memory_database_session: Session):
    # Arrange: Use a non-existent edit_id
    non_existent_edit_id = 9999
    new_name = "Non-Existent Edit Update"
    
    # Act: Attempt to update a non-existent Edit
    updated_edit = update(edit_id=non_existent_edit_id, name=new_name, database_session=memory_database_session)
    
    # Assert: Ensure that the function returns None for a non-existent Edit
    assert updated_edit is None
    
# get edits by group
def test_get_edits_by_groups(memory_database_session: Session):
    edits = get_edits_by_group("11111111-1111-1111-1111-111111111111", memory_database_session)
    
    assert len(edits) == 3
    
def test_get_edits_by_groups_not_success(memory_database_session: Session):
    edits = get_edits_by_group(4123123, memory_database_session)
    
    assert len(edits) == 0
    