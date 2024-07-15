from sqlalchemy.orm import Session
from api.services.edit import create, get
from api.models.database.models import Edit

def test_create(db_session: Session):
    # Define edit data
    song_id = 1
    created_by = 1
    group_id = 1
    name = "Test Edit"
    is_live = True
    
    # Create a new edit
    edit = create(song_id, created_by, group_id, name, is_live, db_session)
    
    # Verify the edit is created and has the correct data
    assert edit is not None
    assert edit.song_id == song_id
    assert edit.created_by == created_by
    assert edit.group_id == group_id
    assert edit.name == name
    assert edit.isLive == is_live

def test_get(db_session: Session):
    # Define edit data
    song_id = 1
    created_by = 1
    group_id = 1
    name = "Test Edit"
    is_live = True
    
    # Create a new edit
    created_edit = create(song_id, created_by, group_id, name, is_live, db_session)
    
    # Fetch the edit by ID
    fetched_edit = get(created_edit.edit_id, db_session)
    
    # Verify the fetched edit matches the created edit
    assert fetched_edit is not None
    assert fetched_edit.edit_id == created_edit.edit_id
    assert fetched_edit.song_id == created_edit.song_id
    assert fetched_edit.created_by == created_edit.created_by
    assert fetched_edit.group_id == created_edit.group_id
    assert fetched_edit.name == created_edit.name
    assert fetched_edit.isLive == created_edit.isLive
    
def test_get_edit_failed(db_session: Session):
    # Define a non-existent edit ID
    non_existent_edit_id = 9999
    
    # Try to fetch the edit by the non-existent ID
    fetched_edit = get(non_existent_edit_id, db_session)
    
    # Verify that no edit is found
    assert fetched_edit is None
