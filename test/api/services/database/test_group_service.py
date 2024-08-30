from sqlalchemy.orm import Session
from api.models.database.model import Group, Edit, Invitation, User
from api.services.database.group import create, get, get_group_by_edit_id, is_group_creator, is_group_member, list_members, remove
from api.mock.database.model import mock_model_memory_links

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
    existing_group = mock_model_memory_links.groups[0]
    
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
    group_id = mock_model_memory_links.groups[0].group_id
    user_id = mock_model_memory_links.users[2].user_id  # User 3 is a member of Group 1
    assert is_group_member(user_id, group_id, db_memory) == True
    
def test_is_group_member_also_creator_true(db_memory: Session):
    group_id = mock_model_memory_links.groups[0].group_id
    user_id = mock_model_memory_links.users[0].user_id  # User 1 is the creator and a member of Group 1
    assert is_group_member(user_id, group_id, db_memory) == True

def test_is_group_member_false(db_memory: Session):
    group_id = mock_model_memory_links.groups[1].group_id
    user_id = mock_model_memory_links.users[0].user_id  # User 1 is not a member of Group 2
    assert is_group_member(user_id, group_id, db_memory) == False

# is_group_creator
def test_is_group_creator_true(db_memory: Session):
    group_id = mock_model_memory_links.groups[0].group_id
    user_id = mock_model_memory_links.users[0].user_id  # User 1 is the creator of Group 1
    assert is_group_creator(user_id, group_id, db_memory) == True

def test_is_group_creator_false(db_memory: Session):
    group_id = mock_model_memory_links.groups[1].group_id
    user_id = mock_model_memory_links.users[0].user_id  # User 1 is not the creator of Group 2
    assert is_group_creator(user_id, group_id, db_memory) == False

def test_is_group_creator_false_not_creator(db_memory: Session):
    group_id = mock_model_memory_links.groups[0].group_id
    user_id = mock_model_memory_links.users[1].user_id  # User 2 is a member but not the creator of Group 1
    assert is_group_creator(user_id, group_id, db_memory) == False
   
    # Arrange: Verwende eine ungültige group_id
    non_existent_group_id = "invalid-group-id"
    
    # Act: Versuche, die Gruppe mit der ungültigen ID zu löschen
    result = remove(non_existent_group_id, db_memory)
    
    # Assert: Stelle sicher, dass keine Gruppe gelöscht wird
    assert result is False
    
def test_remove_group(db_memory: Session):
    # Arrange: Verwende eine vorhandene Gruppe
    existing_group = db_memory.query(Group).first()

    # Act: Lösche die Gruppe
    result = remove(existing_group.group_id, db_memory)

    # Assert: Überprüfe, dass die Gruppe erfolgreich gelöscht wurde
    assert result is True

    # Verify: Stelle sicher, dass die Gruppe nicht mehr in der Datenbank vorhanden ist
    group_in_db = db_memory.query(Group).filter_by(group_id=existing_group.group_id).one_or_none()
    assert group_in_db is None

    # cascading: Group -> Edit, User, Invitation
    edits_in_db = db_memory.query(Edit).filter_by(group_id=existing_group.group_id).all()
    users_in_db = db_memory.query(User).filter_by(group_id=existing_group.group_id).all()
    invitations_in_db = db_memory.query(Invitation).filter_by(group_id=existing_group.group_id).all()
    assert len(edits_in_db) == 0
    assert len(users_in_db) == 0
    assert len(invitations_in_db) == 0

def test_remove_group_failed(db_memory: Session):
    # Arrange: Verwende eine ungültige group_id
    non_existent_group_id = 'non_existent'

    # Act: Versuche, die Gruppe mit der ungültigen ID zu löschen
    result = remove(non_existent_group_id, db_memory)

    # Assert: Stelle sicher, dass keine Gruppe gelöscht wird
    assert result is False

# list_memebers

def test_list_members(db_memory: Session):
    # Arrange: Use an existing group with members
    group_id = mock_model_memory_links.groups[0].group_id  # Assuming Group 1 has members
    
    # Act: List members of the group
    members = list_members(group_id, db_memory)
    
    # Assert: Check that the members are correctly listed
    assert members is not None
    assert len(members) > 0  # Ensure there are members in the group

    # Optional: Check specific members based on your mock data
    assert members[0].user_id == mock_model_memory_links.users[0].user_id  # Creator
    assert members[1].user_id == mock_model_memory_links.users[1].user_id  # Member

def test_list_members_no_members(db_memory: Session):
    # Arrange: Create a new group without any members
    new_group = create("Empty Group", db_memory)  # Create a group without users

    # Act: List members of the new group
    members = list_members(new_group.group_id, db_memory)
    
    # Assert: Check that the member list is empty
    assert members == []  # Ensure no members in the new group
    
def test_get_group_by_edit_id_success(db_memory: Session):
    # Arrange: Verwende eine vorhandene Edit-ID aus den Testdaten
    existing_edit = mock_model_memory_links.edits[0]  # Angenommen, dies ist ein gültiger Edit
    expected_group_id = existing_edit.group_id  # Holen Sie sich die zugehörige group_id

    # Act: Versuchen Sie, die Gruppe anhand der Edit-ID abzurufen
    retrieved_group = get_group_by_edit_id(existing_edit.edit_id, db_memory)

    # Assert: Überprüfen, ob die Gruppe korrekt abgerufen wurde
    assert retrieved_group is not None
    assert retrieved_group.group_id == expected_group_id

def test_get_group_by_edit_id_not_found(db_memory: Session):
    # Arrange: Verwenden Sie eine nicht existierende Edit-ID
    non_existent_edit_id = "non_existent_edit_id"

    # Act: Versuchen Sie, die Gruppe anhand der nicht existierenden Edit-ID abzurufen
    retrieved_group = get_group_by_edit_id(non_existent_edit_id, db_memory)

    # Assert: Überprüfen, dass keine Gruppe abgerufen wurde
    assert retrieved_group is None