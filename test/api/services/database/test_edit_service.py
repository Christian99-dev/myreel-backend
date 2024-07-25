from sqlalchemy.orm import Session
from api.models.database.model import Edit
from api.services.database.edit import create, get, is_edit_creator
from api.utils.database.create_uuid import create_uuid

# create
def test_create(db_session_empty: Session):
    # Arrange: Set up the parameters for the new edit
    song_id = 1  # Ensure this song_id exists in your test setup
    created_by = 1  # Use a valid user_id or create a user if necessary
    group_id = create_uuid()  # Use a valid group_id or create a group if necessary
    name = "Test Edit"
    is_live = True

    # Act: Call the create service function
    new_edit = create(song_id=song_id, created_by=created_by, group_id=group_id, name=name, is_live=is_live, db=db_session_empty)
    
    # Assert: Check the created edit's attributes
    assert new_edit.song_id == song_id
    assert new_edit.created_by == created_by
    assert new_edit.group_id == group_id
    assert new_edit.name == name
    assert new_edit.isLive == is_live

    # Verify: Ensure the edit was actually added to the database
    edit_in_db = db_session_empty.query(Edit).filter_by(edit_id=new_edit.edit_id).one_or_none()
    assert edit_in_db is not None
    assert edit_in_db.song_id == song_id
    assert edit_in_db.created_by == created_by
    assert edit_in_db.group_id == group_id
    assert edit_in_db.name == name
    assert edit_in_db.isLive == is_live

# get    
def test_get(db_session_empty: Session):
    # Define edit data
    song_id = 1
    created_by = 1
    group_id = create_uuid()
    name = "Test Edit"
    is_live = True
    
    # Create a new edit
    created_edit = create(song_id, created_by, group_id, name, is_live, db_session_empty)
    
    # Fetch the edit by ID
    fetched_edit = get(created_edit.edit_id, db_session_empty)
    
    # Verify the fetched edit matches the created edit
    assert fetched_edit is not None
    assert fetched_edit.edit_id == created_edit.edit_id
    assert fetched_edit.song_id == created_edit.song_id
    assert fetched_edit.created_by == created_edit.created_by
    assert fetched_edit.group_id == created_edit.group_id
    assert fetched_edit.name == created_edit.name
    assert fetched_edit.isLive == created_edit.isLive
    
def test_get_edit_failed(db_session_empty: Session):
    # Define a non-existent edit ID
    non_existent_edit_id = 9999
    
    # Try to fetch the edit by the non-existent ID
    fetched_edit = get(non_existent_edit_id, db_session_empty)
    
    # Verify that no edit is found
    assert fetched_edit is None

# is_edit_creator
def test_is_edit_creator_true(db_session_filled: Session):
    # Assuming the creator of Edit 1 in Group 1 has user_id 1
    assert is_edit_creator(1, 1, db_session_filled) == True

def test_is_edit_creator_false(db_session_filled: Session):
    # Assuming Edit 2 in Group 1 was created by a user with user_id 2
    assert is_edit_creator(1, 2, db_session_filled) == False
    