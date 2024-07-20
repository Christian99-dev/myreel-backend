import logging
import time
from datetime import datetime
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from api.utils.middleware.log_access import log_access

class LogAccessMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Zeitpunkt des Zugriffs erfassen
        start_time = time.time()
        access_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Anfrage verarbeiten
        response = await call_next(request)
        
        # Dauer des Anrufs berechnen
        duration = time.time() - start_time
        
        # Log-Nachricht ausgeben
        log_access(request.url.path, response.status_code, duration, access_time)
        
        return response
