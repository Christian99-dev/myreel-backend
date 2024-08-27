from sqlalchemy.orm import Session
from api.models.database.model import Edit, OccupiedSlot
from api.services.database.edit import create, get, is_edit_creator, remove
from api.mock.database.model import model

# create
def test_create(db_memory: Session):
    # Arrange: Verwende vorhandene Testdaten
    song_id = 1  # Existiert in der gefüllten Datenbank
    created_by = 1  # Existiert in der gefüllten Datenbank
    group_id = model.users[0].group_id  # Verwende eine gültige group_id aus den Testdaten
    name = "New Test Edit"
    is_live = True
    video_src = "http://example.com/new_edit.mp4"

    # Act: Erstelle einen neuen Edit
    new_edit = create(song_id=song_id, created_by=created_by, group_id=group_id, name=name, is_live=is_live, video_src=video_src, db=db_memory)
    
    # Assert: Prüfe die Attribute des erstellten Edits
    assert new_edit.song_id == song_id
    assert new_edit.created_by == created_by
    assert new_edit.group_id == group_id
    assert new_edit.name == name
    assert new_edit.isLive == is_live
    assert new_edit.video_src == video_src

    # Verify: Stelle sicher, dass der Edit in der Datenbank gespeichert wurde
    edit_in_db = db_memory.query(Edit).filter_by(edit_id=new_edit.edit_id).one_or_none()
    assert edit_in_db is not None
    assert edit_in_db.song_id == song_id
    assert edit_in_db.created_by == created_by
    assert edit_in_db.group_id == group_id
    assert edit_in_db.name == name
    assert edit_in_db.isLive == is_live
    assert edit_in_db.video_src == video_src

# get    
def test_get(db_memory: Session):
    # Verwende einen vorhandenen Edit aus den Testdaten
    existing_edit = model.edits[0]
    
    # Act: Hole den Edit mit seiner ID
    fetched_edit = get(existing_edit.edit_id, db_memory)
    
    # Assert: Prüfe, ob der gefundene Edit den erwarteten Werten entspricht
    assert fetched_edit is not None
    assert fetched_edit.edit_id == existing_edit.edit_id
    assert fetched_edit.song_id == existing_edit.song_id
    assert fetched_edit.created_by == existing_edit.created_by
    assert fetched_edit.group_id == existing_edit.group_id
    assert fetched_edit.name == existing_edit.name
    assert fetched_edit.isLive == existing_edit.isLive
    assert fetched_edit.video_src == existing_edit.video_src

def test_get_edit_failed(db_memory: Session):
    # Arrange: Verwende eine ungültige edit_id
    non_existent_edit_id = 9999
    
    # Act: Versuche, den Edit mit der ungültigen ID abzurufen
    fetched_edit = get(non_existent_edit_id, db_memory)
    
    # Assert: Stelle sicher, dass kein Edit gefunden wird
    assert fetched_edit is None

# is_edit_creator
def test_is_edit_creator_true(db_memory: Session):
    # Verwende die Datenbank mit bestehenden Daten und prüfe den Ersteller eines Edits
    edit = model.edits[0]  # Zum Beispiel: Edit 1 wurde von User 1 erstellt
    assert is_edit_creator(edit.created_by, edit.edit_id, db_memory) == True

def test_is_edit_creator_false(db_memory: Session):
    # Prüfe einen Fall, bei dem der User nicht der Ersteller des Edits ist
    edit = model.edits[1]  # Zum Beispiel: Edit 2 wurde nicht von User 1 erstellt
    assert is_edit_creator(1, edit.edit_id, db_memory) == False
    
# remove
def test_remove_edit(db_memory: Session):
    # Arrange: Verwende einen vorhandenen Edit
    existing_edit = db_memory.query(Edit).first()

    # Act: Lösche den Edit
    result = remove(existing_edit.edit_id, db_memory)

    # Assert: Überprüfe, dass der Edit erfolgreich gelöscht wurde
    assert result is True

    # Verify: Stelle sicher, dass der Edit nicht mehr in der Datenbank vorhanden ist
    edit_in_db = db_memory.query(Edit).filter_by(edit_id=existing_edit.edit_id).one_or_none()
    assert edit_in_db is None

    # cascading: Edit -> OccupiedSlot
    occupied_slots_in_db = db_memory.query(OccupiedSlot).filter_by(edit_id=existing_edit.edit_id).all()
    assert len(occupied_slots_in_db) == 0

def test_remove_edit_failed(db_memory: Session):
    # Arrange: Verwende eine ungültige edit_id
    non_existent_edit_id = 9999

    # Act: Versuche, den Edit mit der ungültigen ID zu löschen
    result = remove(non_existent_edit_id, db_memory)

    # Assert: Stelle sicher, dass kein Edit gelöscht wird
    assert result is False