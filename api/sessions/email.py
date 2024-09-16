import os
import datetime
import smtplib
from abc import ABC, abstractmethod
from distutils.util import strtobool
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Generator

"""ENV"""
EMAIL_LOCAL = bool(strtobool(os.getenv("EMAIL_LOCAL")))

EMAIL_REMOTE_SMTP_HOST           = os.getenv("EMAIL_REMOTE_SMTP_HOST")
EMAIL_REMOTE_SMTP_SECURE         = bool(strtobool(os.getenv("EMAIL_REMOTE_SMTP_SECURE")))
EMAIL_REMOTE_SMTP_USER           = os.getenv("EMAIL_REMOTE_SMTP_USER")
EMAIL_REMOTE_SMTP_PASSWORD       = os.getenv("EMAIL_REMOTE_SMTP_PASSWORD")
EMAIL_REMOTE_EMAIL_FROM          = os.getenv("EMAIL_REMOTE_EMAIL_FROM")

"""Base Email Session Manager"""
class BaseEmailSessionManager(ABC):

    @abstractmethod
    def __init__(self):
        """Initialisiert den E-Mail-Zugang."""
        pass

    @abstractmethod
    def get_session(self) -> Generator["BaseEmailSessionManager", None, None]:
        """Erzeugt eine E-Mail-Sitzung."""
        pass

    """Session specific methods"""
    @abstractmethod
    def send(self, to: str, subject: str, body: str) -> bool:
        """Sendet eine E-Mail."""
        pass


"""Implementations for Different Email Session Managers"""
class RemoteEmailSessionManager(BaseEmailSessionManager):
    def __init__(self):
        """Initialisiert den Fernzugriff auf E-Mails über SMTP."""

    def get_session(self) -> Generator["BaseEmailSessionManager", None, None]:
        """Erzeugt eine Fern-E-Mail-Sitzung."""
        try:
            print("Starting remote email session")
            yield self
        finally:
            print("Ending remote email session")

    def send(self, to: str, subject: str, body: str) -> bool:
        """Sendet eine E-Mail über SMTP."""
        if not all([EMAIL_REMOTE_SMTP_HOST, EMAIL_REMOTE_SMTP_USER, EMAIL_REMOTE_SMTP_PASSWORD, EMAIL_REMOTE_EMAIL_FROM]):
            raise ValueError("Missing environment variables for SMTP configuration.")
        
        try:
            # Erstelle die E-Mail
            msg = MIMEMultipart()
            msg['From'] = EMAIL_REMOTE_EMAIL_FROM
            msg['To'] = to
            msg['Subject'] = subject
            
            # Textteil der E-Mail
            msg.attach(MIMEText(body, 'plain'))
            
            # Verbindung zum SMTP-Server aufbauen
            if EMAIL_REMOTE_SMTP_SECURE:
                server = smtplib.SMTP_SSL(EMAIL_REMOTE_SMTP_HOST)
            else:
                server = smtplib.SMTP(EMAIL_REMOTE_SMTP_HOST)
                server.starttls()  # Verbindungsverschlüsselung starten, falls nicht SSL

            server.login(EMAIL_REMOTE_SMTP_USER, EMAIL_REMOTE_SMTP_PASSWORD)
            server.sendmail(EMAIL_REMOTE_EMAIL_FROM, to, msg.as_string())
            server.quit()
            
            print("Email sent successfully!")
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

class LocalEmailSessionManager(BaseEmailSessionManager):
    def __init__(self):
        """Initialisiert den lokalen E-Mail-Zugang."""
        self.email_repo = "outgoing/email"
        
        # Sicherstellen, dass der Ordner existiert
        if not os.path.exists(self.email_repo):
            os.makedirs(self.email_repo)

    def get_session(self) -> Generator["BaseEmailSessionManager", None, None]:
        """Erzeugt eine lokale E-Mail-Sitzung."""
        try:
            # print(f"Starting local email session for {self.email_repo}")
            yield self
        finally:
            pass
            # print(f"Ending local email session for {self.email_repo}")

    def send(self, to: str, subject: str, body: str) -> bool:
        """Speichert die E-Mail lokal."""
        try:
            # Erstelle die E-Mail
            msg = MIMEMultipart()
            msg['From'] = "local@test.com"
            msg['To'] = to
            msg['Subject'] = subject
            
            # Textteil der E-Mail
            msg.attach(MIMEText(body, 'plain'))
            
            # Generiere einen Dateinamen mit Zeitstempel
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"email_{timestamp}_to_{to}.eml"
            filepath = os.path.join(self.email_repo, filename)
            
            # Schreibe die E-Mail in die Datei
            with open(filepath, 'w') as file:
                file.write(msg.as_string())
            
            # print(f"Email successfully saved to {filepath}")
            return True
        except Exception as e:
            # print(f"Failed to save email: {e}")
            return False

class MemoryEmailSessionManager(BaseEmailSessionManager):
    def __init__(self):
        """Initialisiert den E-Mail-Speicher im Speicher."""
        pass

    def get_session(self) -> Generator["BaseEmailSessionManager", None, None]:
        """Erzeugt eine transaktionale E-Mail-Sitzung im Speicher."""
        try:
            # print("Starting in-memory email session")
            yield self
        finally:
            pass
            # print("Ending in-memory email session")

    def send(self, to: str, subject: str, body: str) -> bool:
        """Simuliert das Senden einer E-Mail im Speicher."""
        # print(f"Simulating email sent to {to} with subject '{subject}'")
        return True


_email_session_manager = None

def init_email_session_manager():
    global _email_session_manager
    if _email_session_manager is None:
        _email_session_manager = LocalEmailSessionManager() if EMAIL_LOCAL else RemoteEmailSessionManager()


def get_email_session():
    global _email_session_manager
    if _email_session_manager is None:
        return

    try:
        gen = _email_session_manager.get_session() 
        session = next(gen)
        yield session
    except Exception as e:
        raise e
