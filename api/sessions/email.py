import os
import datetime
import smtplib
from abc import ABC, abstractmethod
from distutils.util import strtobool
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Generator

"""ENV"""
LOCAL_EMAIL_ACCESS = bool(strtobool(os.getenv("LOCAL_EMAIL_ACCESS")))

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
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_secure = bool(strtobool(os.getenv("SMTP_SECURE")))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.email_from = os.getenv("EMAIL_FROM")

    def get_session(self) -> Generator["BaseEmailSessionManager", None, None]:
        """Erzeugt eine Fern-E-Mail-Sitzung."""
        try:
            print("Starting remote email session")
            yield self
        finally:
            print("Ending remote email session")

    def send(self, to: str, subject: str, body: str) -> bool:
        """Sendet eine E-Mail über SMTP."""
        if not all([self.smtp_host, self.smtp_user, self.smtp_password, self.email_from]):
            raise ValueError("Missing environment variables for SMTP configuration.")
        
        try:
            # Erstelle die E-Mail
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = to
            msg['Subject'] = subject
            
            # Textteil der E-Mail
            msg.attach(MIMEText(body, 'plain'))
            
            # Verbindung zum SMTP-Server aufbauen
            if self.smtp_secure:
                server = smtplib.SMTP_SSL(self.smtp_host)
            else:
                server = smtplib.SMTP(self.smtp_host)
                server.starttls()  # Verbindungsverschlüsselung starten, falls nicht SSL

            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.email_from, to, msg.as_string())
            server.quit()
            
            print("Email sent successfully!")
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

class LocalEmailSessionManager(BaseEmailSessionManager):
    def __init__(self):
        """Initialisiert den lokalen E-Mail-Zugang."""
        self.email_repo = os.getenv("LOCAL_EMAIL_REPO", "outgoing_emails_test")
        
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

def get_email_session():
    global _email_session_manager
    
    # beim ersten Ausführen
    if _email_session_manager is None:
        _email_session_manager = LocalEmailSessionManager() if LOCAL_EMAIL_ACCESS else RemoteEmailSessionManager()
    
    # Öffnet die Session und gibt sie zurück
    gen = _email_session_manager.get_session()
    session = next(gen)
    yield session
