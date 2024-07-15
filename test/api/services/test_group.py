from sqlalchemy.orm import Session
from api.models.database.model import Group
from api.services.group import create, get

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
