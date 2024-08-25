from sqlalchemy.orm import Session
from api.models.database.model import Group
from api.services.database.group import create, get, is_group_creator, is_group_member
from test.utils.testing_data.db.model import model

# create
def test_create(db_memory: Session):
    name = "Test Group"
    
    # Create a new group
    new_group = create(name, db_memory)
    
    # Verify the group is created and has the correct data
    assert new_group is not None
    assert new_group.name == name
    
    # Verify: Ensure the group was actually added to the database
    group_in_db = db_memory.query(Group).filter_by(group_id=new_group.group_id).one_or_none()
    assert group_in_db is not None
    assert group_in_db.name == name

# get
def test_get(db_memory: Session):
    # Use an existing group from test data
    existing_group = model.groups[0]
    
    # Fetch the group by ID
    fetched_group = get(existing_group.group_id, db_memory)
    
    # Verify the fetched group matches the created group
    assert fetched_group is not None
    assert fetched_group.group_id == existing_group.group_id
    assert fetched_group.name == existing_group.name
    
def test_get_group_failed(db_memory: Session):
    # Define a non-existent group ID
    non_existent_group_id = 9999
    
    # Try to fetch the group by the non-existent ID
    fetched_group = get(non_existent_group_id, db_memory)
    
    # Verify that no group is found
    assert fetched_group is None

# is_group_member
def test_is_group_member_true(db_memory: Session):
    group_id = model.groups[0].group_id
    user_id = model.users[2].user_id  # User 3 is a member of Group 1
    assert is_group_member(user_id, group_id, db_memory) == True
    
def test_is_group_member_also_creator_true(db_memory: Session):
    group_id = model.groups[0].group_id
    user_id = model.users[0].user_id  # User 1 is the creator and a member of Group 1
    assert is_group_member(user_id, group_id, db_memory) == True

def test_is_group_member_false(db_memory: Session):
    group_id = model.groups[1].group_id
    user_id = model.users[0].user_id  # User 1 is not a member of Group 2
    assert is_group_member(user_id, group_id, db_memory) == False

# is_group_creator
def test_is_group_creator_true(db_memory: Session):
    group_id = model.groups[0].group_id
    user_id = model.users[0].user_id  # User 1 is the creator of Group 1
    assert is_group_creator(user_id, group_id, db_memory) == True

def test_is_group_creator_false(db_memory: Session):
    group_id = model.groups[1].group_id
    user_id = model.users[0].user_id  # User 1 is not the creator of Group 2
    assert is_group_creator(user_id, group_id, db_memory) == False

def test_is_group_creator_false_not_creator(db_memory: Session):
    group_id = model.groups[0].group_id
    user_id = model.users[1].user_id  # User 2 is a member but not the creator of Group 1
    assert is_group_creator(user_id, group_id, db_memory) == False