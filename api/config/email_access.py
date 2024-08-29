import datetime
from distutils.util import strtobool
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
from abc import ABC, abstractmethod

LOCAL_EMAIL_ACCESS = bool(strtobool(os.getenv("LOCAL_EMAIL_ACCESS")))

class BaseEmailAccess(ABC):
    @abstractmethod
    def send(self, to: str, subject: str, body: str) -> bool:
        pass

class RemoteEmailAccess(BaseEmailAccess):
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_secure = bool(strtobool(os.getenv("SMTP_SECURE")))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.email_from = os.getenv("EMAIL_FROM")
    
    def send(self, to: str, subject: str, body: str) -> bool:
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
         
class LocalEmailAccess(BaseEmailAccess):
    def __init__(self):
        self.email_repo = os.getenv("LOCAL_EMAIL_REPO", "outgoing_emails_test")
        
        # Sicherstellen, dass der Ordner existiert
        if not os.path.exists(self.email_repo):
            os.makedirs(self.email_repo)
    
    def send(self, to: str, subject: str, body: str) -> bool:
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
            
            print(f"Email successfully saved to {filepath}")
            return True
        except Exception as e:
            print(f"Failed to save email: {e}")
            return False
    
class MemoryEmailAcccess(BaseEmailAccess):
    def send(self, to: str, subject: str, body: str) -> bool:
        # print("email.send() memory")
        pass

email_access = LocalEmailAccess() if LOCAL_EMAIL_ACCESS else RemoteEmailAccess()

def get_email_access(): 
    return email_access
