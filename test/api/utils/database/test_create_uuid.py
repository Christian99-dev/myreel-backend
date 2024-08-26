import re
from api.utils.database.create_uuid import create_uuid

def test_create_uuid():
    uuid_str = create_uuid()

    # Test the length of the encoded UUID
    assert len(uuid_str) == 22, "UUID should be 22 characters long"

    # Ensure that the UUID contains only URL-safe characters
    assert re.match(r'^[A-Za-z0-9_-]+$', uuid_str), "UUID contains invalid characters"

    # Ensure that no padding ('=') exists in the UUID string
    assert '=' not in uuid_str, "UUID should not contain padding ('=')"

    # Additional test to ensure uniqueness (optional)
    uuid_str2 = create_uuid()
    assert uuid_str != uuid_str2, "UUIDs should be unique"