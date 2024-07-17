from sqlalchemy.orm import Session
from api.models.database.model import Group
from api.services.group import create, get, is_group_creator

# create
def test_create(db_session: Session):
    # Define group data
    name = "Test Group"
    
    # Create a new group
    new_group = create(name, db_session)
    
    # Verify the group is created and has the correct data
    assert new_group is not None
    assert new_group.name == name
    
    # Verify: Ensure the group was actually added to the database
    group_in_db = db_session.query(Group).filter_by(group_id=new_group.group_id).one_or_none()
    assert group_in_db is not None
    assert group_in_db.name == name

# get
def test_get(db_session: Session):
    # Define group data
    name = "Test Group"
    
    # Create a new group
    created_group = create(name, db_session)
    
    # Fetch the group by ID
    fetched_group = get(created_group.group_id, db_session)
    
    # Verify the fetched group matches the created group
    assert fetched_group is not None
    assert fetched_group.group_id == created_group.group_id
    assert fetched_group.name == created_group.name
    
def test_get_group_failed(db_session: Session):
    # Define a non-existent group ID
    non_existent_group_id = 9999
    
    # Try to fetch the group by the non-existent ID
    fetched_group = get(non_existent_group_id, db_session)
    
    # Verify that no group is found
    assert fetched_group is None

# is_group_creator
def test_is_group_creator_true(db_session_filled: Session):
    # Assuming the creator of Group 1 has user_id 1
    assert is_group_creator(1, 1, db_session_filled) == True

def test_is_group_creator_false_not_in_group(db_session_filled: Session):
    # Assuming user_id 1 is not in Group 2
    assert is_group_creator(1, 2, db_session_filled) == False

def test_is_group_creator_false_not_creator(db_session_filled: Session):
    # Assuming a member of Group 1 with user_id 2 is not the creator
    assert is_group_creator(2, 1, db_session_filled) == False