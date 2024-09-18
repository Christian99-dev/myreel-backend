import pytest

from api.exceptions.email import EmailDeliveryError
from api.services.email.invite import invite
from api.sessions.email import MemoryEmailSessionManager


# Positiver Test für invite
def test_invite_success(memory_email_session: MemoryEmailSessionManager):
    """Testet, dass die Einladung erfolgreich gesendet wird."""
    
    # Arrange: Erstelle Testdaten
    to = "test@example.com"
    code = "123456"
    invite_id = "invite123"
    groupid = "group456"

    # Act & Assert: Stelle sicher, dass die Methode erfolgreich ausgeführt wird
    try:
        invite(to, code, invite_id, groupid, memory_email_session)
    except EmailDeliveryError:
        pytest.fail("EmailDeliveryError sollte nicht auftreten, wenn die E-Mail erfolgreich gesendet wird.")

# Negativer Test für invite (kein Empfänger)
def test_invite_no_recipient(memory_email_session: MemoryEmailSessionManager):
    """Testet, dass invite eine Exception auslöst, wenn keine Empfängeradresse angegeben wird."""
    
    # Arrange: Leere Empfängeradresse
    to = ""
    code = "123456"
    invite_id = "invite123"
    groupid = "group456"

    # Act & Assert: Erwartet einen Fehler
    with pytest.raises(EmailDeliveryError, match="Recipient email address is missing."):
        invite(to, code, invite_id, groupid, memory_email_session)

