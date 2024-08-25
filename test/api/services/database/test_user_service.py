from sqlalchemy.orm import Session
from api.models.database.model import User
from api.services.database.user import create, get
from api.utils.database.create_uuid import create_uuid
from test.utils.testing_data.db.model import model

# create
def test_create(db_memory: Session):
    # Define user data
    group_id = create_uuid()
    role = "admin"
    name = "Test User"
    email = "testuser@example.com"
    
    # Create a new user
    new_user = create(group_id, role, name, email, db_memory)
    
    # Verify the user is created and has the correct data
    assert new_user is not None
    assert new_user.name == name
    assert new_user.email == email
    assert new_user.role == role
    assert new_user.group_id == group_id
    
    # Verify: Ensure the user was actually added to the database
    user_in_db = db_memory.query(User).filter_by(user_id=new_user.user_id).one_or_none()
    assert user_in_db is not None
    assert user_in_db.group_id == group_id
    assert user_in_db.role == role
    assert user_in_db.name == name
    assert user_in_db.email == email

# get
def test_get(db_memory: Session):
    # Assume the first user from the test data is used
    user_id = model.users[0].user_id
    retrieved_user = get(user_id, db_memory)
    
    assert retrieved_user is not None
    assert retrieved_user.user_id == user_id
    assert retrieved_user.name == model.users[0].name
    assert retrieved_user.email == model.users[0].email
    assert retrieved_user.role == model.users[0].role
    assert retrieved_user.group_id == model.users[0].group_id
    
def test_get_user_failed(db_memory: Session):
    # Define a non-existent user ID
    non_existent_user_id = 9999
    
    # Try to fetch the user by the non-existent ID
    fetched_user = get(non_existent_user_id, db_memory)
    
    # Verify that no user is found
    assert fetched_user is None
