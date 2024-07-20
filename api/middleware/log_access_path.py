# middlewares.py

import logging
import time
from datetime import datetime
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Logger konfigurieren
logger = logging.getLogger("access")

class LogAccessMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Zeitpunkt des Zugriffs erfassen
        start_time = time.time()
        access_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Request verarbeiten
        response = await call_next(request)
        
        # Dauer des Anrufs berechnen
        duration = time.time() - start_time
        
        # Log-Nachricht formatieren
        log_message = (
            f"Access time: {access_time}, "
            f"Path: {request.url.path}, "
            f"Status: {response.status_code}, "
            f"Duration: {duration:.4f} seconds"
        )
        
        # Log-Nachricht ausgeben
        logger.info(log_message)
        
        return response
