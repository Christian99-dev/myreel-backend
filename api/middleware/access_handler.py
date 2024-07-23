from datetime import datetime
from typing import Dict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from api.auth.role_enum import RoleEnum
from api.utils.middleware.get_all_routes import get_all_routes
from api.utils.middleware.log_access import log_access

class AccessHandlerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, path_roles: Dict[str, RoleEnum]):
        super().__init__(app)
        self.path_roles = path_roles

    async def dispatch(self, request: Request, call_next):
        
        app             = request.app
        incoming_role   = RoleEnum.EDIT_CREATOR
        required_role   = RoleEnum.EDIT_CREATOR
        all_routes      = get_all_routes(app)
        path_roles      = self.path_roles
        
        if 1 == 1:  
            log_access(request.url.path, 403, 0.0000, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"Role conflict! Role: {incoming_role.name}, Required: {required_role.name}")
            return Response(status_code=403)
                
        return await call_next(request)