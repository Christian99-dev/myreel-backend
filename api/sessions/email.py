import datetime
import logging
import os
import smtplib
from abc import ABC, abstractmethod
from distutils.util import strtobool
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Generator

logger = logging.getLogger("sessions.email")

"""ENV"""
EMAIL_LOCAL = bool(strtobool(os.getenv("EMAIL_LOCAL")))

EMAIL_REMOTE_SMTP_HOST = os.getenv("EMAIL_REMOTE_SMTP_HOST")
EMAIL_REMOTE_SMTP_SECURE = bool(strtobool(os.getenv("EMAIL_REMOTE_SMTP_SECURE")))
EMAIL_REMOTE_SMTP_USER = os.getenv("EMAIL_REMOTE_SMTP_USER")
EMAIL_REMOTE_SMTP_PASSWORD = os.getenv("EMAIL_REMOTE_SMTP_PASSWORD")
EMAIL_REMOTE_EMAIL_FROM = os.getenv("EMAIL_REMOTE_EMAIL_FROM")

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
        logger.info(f"__init__(): (remote)")

    def get_session(self) -> Generator["BaseEmailSessionManager", None, None]:
        """Erzeugt eine Fern-E-Mail-Sitzung."""
        logger.info(f"get_session(): (remote)")
        try:
            yield self
        finally:
            logger.info(f"get_session(): closed session (remote)")

    def send(self, to: str, subject: str, body: str) -> bool:
        """Sendet eine E-Mail über SMTP."""
        if not all([EMAIL_REMOTE_SMTP_HOST, EMAIL_REMOTE_SMTP_USER, EMAIL_REMOTE_SMTP_PASSWORD, EMAIL_REMOTE_EMAIL_FROM]):
            logger.error("send(): Missing environment variables for SMTP configuration.")
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
                logger.info(f"send(): Using secure SMTP connection")
            else:
                server = smtplib.SMTP(EMAIL_REMOTE_SMTP_HOST)
                server.starttls()  # Verbindungsverschlüsselung starten, falls nicht SSL
                logger.info(f"send(): Using non-secure SMTP connection with STARTTLS")

            server.login(EMAIL_REMOTE_SMTP_USER, EMAIL_REMOTE_SMTP_PASSWORD)
            logger.info(f"send(): Logged in to SMTP server")
            server.sendmail(EMAIL_REMOTE_EMAIL_FROM, to, msg.as_string())
            server.quit()
            
            logger.info(f"send(): Email sent successfully to {to}")
            return True
        except Exception as e:
            logger.error(f"send(): Failed to send email: {e}")
            return False


class LocalEmailSessionManager(BaseEmailSessionManager):
    def __init__(self):
        """Initialisiert den lokalen E-Mail-Zugang."""
        logger.info(f"__init__(): (local)")
        self.email_repo = "outgoing/email"
        
        # Sicherstellen, dass der Ordner existiert
        if not os.path.exists(self.email_repo):
            os.makedirs(self.email_repo)
            logger.info(f"__init__(): Created local email storage directory at {self.email_repo}")

    def get_session(self) -> Generator["BaseEmailSessionManager", None, None]:
        """Erzeugt eine lokale E-Mail-Sitzung."""
        logger.info(f"get_session(): (local)")
        try:
            yield self
        finally:
            logger.info(f"get_session(): closed session (local)")

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
            
            logger.info(f"send(): Email successfully saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"send(): Failed to save email: {e}")
            return False


class MemoryEmailSessionManager(BaseEmailSessionManager):
    def __init__(self):
        """Initialisiert den E-Mail-Speicher im Speicher."""
        logger.info(f"__init__(): (memory)")

    def get_session(self) -> Generator["BaseEmailSessionManager", None, None]:
        """Erzeugt eine transaktionale E-Mail-Sitzung im Speicher."""
        logger.info(f"get_session(): (memory)")
        try:
            yield self
        finally:
            logger.info(f"get_session(): closed session (memory)")

    def send(self, to: str, subject: str, body: str) -> bool:
        """Simuliert das Senden einer E-Mail im Speicher."""
        logger.info(f"send(): Simulating email sent to {to} with subject '{subject}'")
        return True


_email_session_manager = None

def init_email_session_manager():
    global _email_session_manager
    logger.info(f"init_email_session_manager()")
    
    if _email_session_manager is None:
        _email_session_manager = LocalEmailSessionManager() if EMAIL_LOCAL else RemoteEmailSessionManager()
    else:
        logger.warning(f"init_email_session_manager(): already initialized")


def get_email_session():
    global _email_session_manager
    logger.info(f"get_email_session()")
    
    if _email_session_manager is None:
        logger.error(f"get_email_session(): failed! manager not initialized")
        return

    try:
        gen = _email_session_manager.get_session()
        session = next(gen)
        yield session
    except Exception as e:
        logger.error(f"get_email_session(): Error: {e}")
        raise e
