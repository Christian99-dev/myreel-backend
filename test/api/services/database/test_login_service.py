from datetime import datetime, timedelta
from api.models.database.model import LoginRequest
from api.services.database.login import create, delete
from api.mock.database.model import model

# create
def test_create(db_memory):
    user_id = model.users[3].user_id  # Use the fourth user
    login_request = create(user_id=user_id, db=db_memory)

    assert login_request.user_id == user_id
    assert isinstance(login_request.pin, str)
    assert login_request.created_at <= datetime.now()
    assert login_request.expires_at == login_request.created_at + timedelta(minutes=10)

# delete
def test_delete(db_memory):
    user_id = model.users[3].user_id  # Use the fourth user
    login_request = create(user_id=user_id, db=db_memory)

    # Ensure the login request exists
    assert db_memory.query(LoginRequest).filter(LoginRequest.user_id == user_id).first() is not None

    # Delete the login request
    delete(user_id=user_id, db=db_memory)

    # Ensure the login request no longer exists
    assert db_memory.query(LoginRequest).filter(LoginRequest.user_id == user_id).first() is None
