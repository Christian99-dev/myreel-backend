from sqlalchemy.orm import Session
from api.services.user import create, get

def test_create(db_session: Session):
    # Define user data
    group_id = 1
    role = "admin"
    name = "Test User"
    email = "testuser@example.com"
    
    # Create a new user
    user = create(group_id, role, name, email, db_session)
    
    # Verify the user is created and has the correct data
    assert user is not None
    assert user.name == name
    assert user.email == email
    assert user.role == role
    assert user.group_id == group_id

def test_get(db_session: Session):
    # Define user data
    group_id = 1
    role = "admin"
    name = "Test User"
    email = "testuser@example.com"
    
    # Create a new user
    created_user = create(group_id, role, name, email, db_session)
    
    # Fetch the user by ID
    fetched_user = get(created_user.user_id, db_session)
    
    # Verify the fetched user matches the created user
    assert fetched_user is not None
    assert fetched_user.user_id == created_user.user_id
    assert fetched_user.name == created_user.name
    assert fetched_user.email == created_user.email
    assert fetched_user.role == created_user.role
    assert fetched_user.group_id == created_user.group_id
    
    
def test_get_user_failed(db_session: Session):
    # Define a non-existent user ID
    non_existent_user_id = 9999
    
    # Try to fetch the user by the non-existent ID
    fetched_user = get(non_existent_user_id, db_session)
    
    # Verify that no user is found
    assert fetched_user is None
