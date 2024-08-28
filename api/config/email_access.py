import os
from abc import ABC, abstractmethod
from distutils.util import strtobool
import os


LOCAL_EMAIL_ACCESS = strtobool(os.getenv("LOCAL_EMAIL_ACCESS"))

class BaseEmailAccess(ABC):
    @abstractmethod
    def send(self) -> bool:
        pass

class RemoteEmailAcccess(BaseEmailAccess):
    def send(self):
        print("email.send() remote")
        pass
    
class LocalEmailAcccess(BaseEmailAccess):
    def send(self):
        print("email.send() local")
        pass
    
class MemoryEmailAcccess(BaseEmailAccess):
    def send(self):
        print("email.send() memory")
        pass

email_access = LocalEmailAcccess() if LOCAL_EMAIL_ACCESS else RemoteEmailAcccess()
