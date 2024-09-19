import pytest

from api.exceptions.sessions.email import EmailDeliveryError
from api.sessions.email import MemoryEmailSessionManager


# Positiver Fall: Testet das erfolgreiche Senden der E-Mail
def test_memory_email_send_success(memory_email_session: MemoryEmailSessionManager):
    """Testet, dass die E-Mail im Speicher erfolgreich gesendet wird."""
    
    # Arrange: Erstelle die Testdaten
    to_address = "test@example.com"
    subject = "Test Email"
    body = "This is a test email."

    # Act: Versuche, die E-Mail zu senden
    try:
        memory_email_session.send(to_address, subject, body)
    except EmailDeliveryError:
        pytest.fail("EmailDeliveryError sollte für einen erfolgreichen Versand nicht auftreten.")

# Negativer Fall: Testet eine E-Mail ohne Empfänger (dies sollte einen Fehler auslösen)
def test_memory_email_send_no_recipient(memory_email_session: MemoryEmailSessionManager):
    """Testet, dass das Senden einer E-Mail ohne Empfänger einen Fehler auslöst."""
    
    # Arrange: Erstelle eine E-Mail ohne Empfänger
    to_address = ""  # Kein Empfänger
    subject = "Test Email"
    body = "This email has no recipient."

    # Act & Assert: Ein Fehler sollte ausgelöst werden
    with pytest.raises(EmailDeliveryError):
        memory_email_session.send(to_address, subject, body)

# Negativer Fall: Testet das Senden einer E-Mail ohne Betreff (dies sollte einen Fehler auslösen)
def test_memory_email_send_no_subject(memory_email_session: MemoryEmailSessionManager):
    """Testet, dass das Senden einer E-Mail ohne Betreff einen Fehler auslöst."""
    
    # Arrange: Erstelle eine E-Mail ohne Betreff
    to_address = "test@example.com"
    subject = ""  # Kein Betreff
    body = "This email has no subject."

    # Act & Assert: Ein Fehler sollte ausgelöst werden
    with pytest.raises(EmailDeliveryError):
        memory_email_session.send(to_address, subject, body)

# Negativer Fall: Testet das Senden einer E-Mail ohne Nachrichtentext (dies sollte einen Fehler auslösen)
def test_memory_email_send_no_body(memory_email_session: MemoryEmailSessionManager):
    """Testet, dass das Senden einer E-Mail ohne Nachrichtentext einen Fehler auslöst."""
    
    # Arrange: Erstelle eine E-Mail ohne Nachrichtentext
    to_address = "test@example.com"
    subject = "Test Email"
    body = ""  # Kein Nachrichtentext

    # Act & Assert: Ein Fehler sollte ausgelöst werden
    with pytest.raises(EmailDeliveryError):
        memory_email_session.send(to_address, subject, body)
