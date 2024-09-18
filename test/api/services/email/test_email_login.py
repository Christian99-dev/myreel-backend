import pytest

from api.exceptions.email import EmailDeliveryError
from api.services.email.login import login
from api.sessions.email import MemoryEmailSessionManager


# Positiver Test für login
def test_login_success(memory_email_session: MemoryEmailSessionManager):
    """Testet, dass der Login-Code erfolgreich gesendet wird."""
    
    # Arrange: Erstelle Testdaten
    to = "test@example.com"
    code = "123456"

    # Act & Assert: Stelle sicher, dass die Methode erfolgreich ausgeführt wird
    try:
        login(to, code, memory_email_session)
    except EmailDeliveryError:
        pytest.fail("EmailDeliveryError sollte nicht auftreten, wenn die E-Mail erfolgreich gesendet wird.")

# Negativer Test für login (kein Empfänger)
def test_login_no_recipient(memory_email_session: MemoryEmailSessionManager):
    """Testet, dass login eine Exception auslöst, wenn keine Empfängeradresse angegeben wird."""
    
    # Arrange: Leere Empfängeradresse
    to = ""
    code = "123456"

    # Act & Assert: Erwartet einen Fehler
    with pytest.raises(EmailDeliveryError, match="Recipient email address is missing."):
        login(to, code, memory_email_session)
