from sqlalchemy.orm import Session
from api.models.database.model import Group, Edit, Invitation, User
from api.services.database.group import create, get, get_group_by_edit_id, get_group_by_user_id, is_group_creator, is_group_member, list_members, remove
from mock.database.data import data
# create
def test_create(memory_database_session: Session):
    name = "Test Group"
    
    # Create a new group
    new_group = create(name, memory_database_session)
    
    # Verify the group is created and has the correct data
    assert new_group is not None
    assert new_group.name == name
    
    # Verify: Ensure the group was actually added to the database
    group_in_database_session = memory_database_session.query(Group).filter_by(group_id=new_group.group_id).one_or_none()
    assert group_in_database_session is not None
    assert group_in_database_session.name == name

# get
def test_get(memory_database_session: Session):
    # Use an existing group from test data
    existing_group = data["groups"][0]
    
    # Fetch the group by ID
    fetched_group = get(existing_group["group_id"], memory_database_session)
    
    # Verify the fetched group matches the created group
    assert fetched_group is not None
    assert fetched_group.group_id == existing_group["group_id"]
    assert fetched_group.name == existing_group["name"]
    
def test_get_group_failed(memory_database_session: Session):
    # Define a non-existent group ID
    non_existent_group_id = 9999
    
    # Try to fetch the group by the non-existent ID
    fetched_group = get(non_existent_group_id, memory_database_session)
    
    # Verify that no group is found
    assert fetched_group is None

# is_group_member
def test_is_group_member_true(memory_database_session: Session):
    group_id = "11111111-1111-1111-1111-111111111111"
    user_id = data["users"][2]["user_id"]  # User 3 is a member of Group 1
    assert is_group_member(user_id, group_id, memory_database_session) == True
    
def test_is_group_member_also_creator_true(memory_database_session: Session):
    group_id = "11111111-1111-1111-1111-111111111111"
    user_id = data["users"][0]["user_id"]  # User 1 is the creator and a member of Group 1
    assert is_group_member(user_id, group_id, memory_database_session) == True

def test_is_group_member_false(memory_database_session: Session):
    group_id = data["groups"][1]["group_id"]
    user_id = data["users"][0]["user_id"]  # User 1 is not a member of Group 2
    assert is_group_member(user_id, group_id, memory_database_session) == False

# is_group_creator
def test_is_group_creator_true(memory_database_session: Session):
    group_id = "11111111-1111-1111-1111-111111111111"
    user_id = data["users"][0]["user_id"]  # User 1 is the creator of Group 1
    assert is_group_creator(user_id, group_id, memory_database_session) == True

def test_is_group_creator_false(memory_database_session: Session):
    group_id = data["groups"][1]["group_id"]
    user_id = data["users"][0]["user_id"]  # User 1 is not the creator of Group 2
    assert is_group_creator(user_id, group_id, memory_database_session) == False

def test_is_group_creator_false_not_creator(memory_database_session: Session):
    group_id = "11111111-1111-1111-1111-111111111111"
    user_id = data["users"][1]["user_id"]  # User 2 is a member but not the creator of Group 1
    assert is_group_creator(user_id, group_id, memory_database_session) == False
   
    # Arrange: Verwende eine ungültige group_id
    non_existent_group_id = "invalid-group-id"
    
    # Act: Versuche, die Gruppe mit der ungültigen ID zu löschen
    result = remove(non_existent_group_id, memory_database_session)
    
    # Assert: Stelle sicher, dass keine Gruppe gelöscht wird
    assert result is False
    
def test_remove_group(memory_database_session: Session):
    # Arrange: Verwende eine vorhandene Gruppe
    existing_group = memory_database_session.query(Group).first()

    # Act: Lösche die Gruppe
    result = remove(existing_group.group_id, memory_database_session)

    # Assert: Überprüfe, dass die Gruppe erfolgreich gelöscht wurde
    assert result is True

    # Verify: Stelle sicher, dass die Gruppe nicht mehr in der Datenbank vorhanden ist
    group_in_database_session = memory_database_session.query(Group).filter_by(group_id=existing_group.group_id).one_or_none()
    assert group_in_database_session is None

    # cascading: Group -> Edit, User, Invitation
    edits_in_database_session = memory_database_session.query(Edit).filter_by(group_id=existing_group.group_id).all()
    users_in_database_session = memory_database_session.query(User).filter_by(group_id=existing_group.group_id).all()
    invitations_in_database_session = memory_database_session.query(Invitation).filter_by(group_id=existing_group.group_id).all()
    assert len(edits_in_database_session) == 0
    assert len(users_in_database_session) == 0
    assert len(invitations_in_database_session) == 0

def test_remove_group_failed(memory_database_session: Session):
    # Arrange: Verwende eine ungültige group_id
    non_existent_group_id = 'non_existent'

    # Act: Versuche, die Gruppe mit der ungültigen ID zu löschen
    result = remove(non_existent_group_id, memory_database_session)

    # Assert: Stelle sicher, dass keine Gruppe gelöscht wird
    assert result is False

# list_memebers

def test_list_members(memory_database_session: Session):
    # Arrange: Use an existing group with members
    group_id = "11111111-1111-1111-1111-111111111111"  # Assuming Group 1 has members
    
    # Act: List members of the group
    members = list_members(group_id, memory_database_session)
    
    # Assert: Check that the members are correctly listed
    assert members is not None
    assert len(members) > 0  # Ensure there are members in the group

    # Optional: Check specific members based on your mock data
    assert members[0].user_id == data["users"][0]["user_id"]  # Creator
    assert members[1].user_id == data["users"][1]["user_id"]  # Member

def test_list_members_no_members(memory_database_session: Session):
    # Arrange: Create a new group without any members
    new_group = create("Empty Group", memory_database_session)  # Create a group without users

    # Act: List members of the new group
    members = list_members(new_group.group_id, memory_database_session)
    
    # Assert: Check that the member list is empty
    assert members == []  # Ensure no members in the new group
   
# test get group by email 
def test_get_group_by_edit_id_success(memory_database_session: Session):
    # Arrange: Verwende eine vorhandene Edit-ID aus den Testdaten
    existing_edit = data["edits"][0]  # Angenommen, dies ist ein gültiger Edit
    expected_group_id = existing_edit["group_id"]  # Holen Sie sich die zugehörige group_id

    # Act: Versuchen Sie, die Gruppe anhand der Edit-ID abzurufen
    retrieved_group = get_group_by_edit_id(existing_edit["edit_id"], memory_database_session)

    # Assert: Überprüfen, ob die Gruppe korrekt abgerufen wurde
    assert retrieved_group is not None
    assert retrieved_group.group_id == expected_group_id

def test_get_group_by_edit_id_not_found(memory_database_session: Session):
    # Arrange: Verwenden Sie eine nicht existierende Edit-ID
    non_existent_edit_id = "non_existent_edit_id"

    # Act: Versuchen Sie, die Gruppe anhand der nicht existierenden Edit-ID abzurufen
    retrieved_group = get_group_by_edit_id(non_existent_edit_id, memory_database_session)

    # Assert: Überprüfen, dass keine Gruppe abgerufen wurde
    assert retrieved_group is None
    
    # test get_group by user id
def test_get_group_by_user_id_success(memory_database_session: Session):
    # Arrange: Use an existing user with a valid group
    existing_user = data["users"][0]  # Assuming User 1 is in Group 1
    expected_group_id = existing_user["group_id"]  # Get the associated group_id

    # Act: Attempt to retrieve the group by the user's ID
    retrieved_group = get_group_by_user_id(existing_user["user_id"], memory_database_session)

    # Assert: Verify that the correct group is retrieved
    assert retrieved_group is not None
    assert retrieved_group.group_id == expected_group_id

def test_get_group_by_user_id_not_found(memory_database_session: Session):
    # Arrange: Use a non-existent user ID
    non_existent_user_id = 9999

    # Act: Attempt to retrieve the group by the non-existent user's ID
    retrieved_group = get_group_by_user_id(non_existent_user_id, memory_database_session)

    # Assert: Verify that no group is returned
    assert retrieved_group is None