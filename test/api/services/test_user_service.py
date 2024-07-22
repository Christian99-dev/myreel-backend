from sqlalchemy.orm import Session
from api.models.database.model import User
from api.services.user import create, get
from api.utils.database.create_uuid import create_uuid

# create
def test_create(db_session_empty: Session):
    # Define user data
    group_id = create_uuid()
    role = "admin"
    name = "Test User"
    email = "testuser@example.com"
    
    # Create a new user
    new_user = create(group_id, role, name, email, db_session_empty)
    
    # Verify the user is created and has the correct data
    assert new_user is not None
    assert new_user.name == name
    assert new_user.email == email
    assert new_user.role == role
    assert new_user.group_id == group_id
    
    # Verify: Ensure the user was actually added to the database
    user_in_db = db_session_empty.query(User).filter_by(user_id=new_user.user_id).one_or_none()
    assert user_in_db is not None
    assert user_in_db.group_id == group_id
    assert user_in_db.role == role
    assert user_in_db.name == name
    assert user_in_db.email == email

# get
def test_get(db_session_empty: Session):
    # Define user data
    group_id = create_uuid()
    role = "admin"
    name = "Test User"
    email = "testuser@example.com"
    
    # Create a new user
    created_user = create(group_id, role, name, email, db_session_empty)
    
    # Fetch the user by ID
    fetched_user = get(created_user.user_id, db_session_empty)
    
    # Verify the fetched user matches the created user
    assert fetched_user is not None
    assert fetched_user.user_id == created_user.user_id
    assert fetched_user.name == created_user.name
    assert fetched_user.email == created_user.email
    assert fetched_user.role == created_user.role
    assert fetched_user.group_id == created_user.group_id
      
def test_get_user_failed(db_session_empty: Session):
    # Define a non-existent user ID
    non_existent_user_id = 9999
    
    # Try to fetch the user by the non-existent ID
    fetched_user = get(non_existent_user_id, db_session_empty)
    
    # Verify that no user is found
    assert fetched_user is None
