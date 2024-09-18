class EmailSendError(Exception):
    """Generische Ausnahme für Fehler beim Senden von E-Mails."""
    pass

class EmailConfigurationError(EmailSendError):
    """Ausnahme für Fehler in der E-Mail-Konfiguration."""
    pass

class EmailConnectionError(EmailSendError):
    """Ausnahme für Verbindungsprobleme mit dem SMTP-Server."""
    pass

class EmailDeliveryError(EmailSendError):
    """Ausnahme für Probleme beim Übermitteln der E-Mail."""
    pass
