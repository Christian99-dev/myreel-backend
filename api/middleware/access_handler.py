import logging
from datetime import datetime
from typing import Callable, Dict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from api.auth import jwt
from api.auth.role import Role, RoleInfos
from api.config.path_roles import PathInfo
from api.utils.middleware.log_access import log_access
from api.utils.routes.extract_role_credentials_from_request import extract_role_credentials_from_request

testing_logger = logging.getLogger("testing")

class AccessHandlerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, path_roles: Dict[str, PathInfo], get_db: Callable):
        super().__init__(app)
        self.path_roles = path_roles
        self.get_db = get_db

    async def dispatch(self, request: Request, call_next):
        pathInfo        = self.path_roles.get(request.url.path)
        
        if pathInfo is None:
            return Response(status_code=404)
            
        # all cred
        credentials = extract_role_credentials_from_request(request)
        
        admintoken  = credentials.admintoken
        groupid     = credentials.groupid
        editid      = credentials.editid
        
        # user id from jwt
        userid = None
        try:
            userid = jwt.read_jwt(credentials.jwt)
        except Exception as e:            
            userid = None
        
        # init role object
        db_generator = self.get_db()
        db_session = next(db_generator)
        
        role = Role(role_infos=RoleInfos(admintoken=admintoken, userid=userid, groupid=groupid, editid=editid), db_session=db_session)
        testing_logger.debug(f"Incoming: {role._role}, Required: {pathInfo.role}, Subroles: {pathInfo.has_subroles}, Path: {request.url.path}, hasAccess: {role.hasAccess(pathInfo)}")
        if role.hasAccess(pathInfo) is False:  
            log_access(request.url.path, 403, 0.0000, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"Role conflict! Role: {role._role}, Required: {pathInfo.role}")
            return Response(status_code=403)
                
        return await call_next(request)