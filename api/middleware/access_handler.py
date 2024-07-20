from datetime import datetime
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from api.auth.role import RoleEnum
from api.utils.middleware.log_access import log_access

class AccessHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        
        incoming_role = RoleEnum.EDIT_CREATOR
        required_role = RoleEnum.EDIT_CREATOR
    
        if 1 == 2:  
            log_access(request.url.path, 403, 0.0000, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"Role conflict! Role: {incoming_role.name}, Required: {required_role.name}")
            return Response(status_code=403)
                
        return await call_next(request)