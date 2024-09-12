import logging
from datetime import datetime
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from api.utils.jwt import jwt
from api.config.endpoints import EndpointConfig
from api.security.role_class import Role, RoleInfos
from api.utils.middleware.log_access import log_access
from api.utils.routes.extract_role_credentials_from_request import extract_role_credentials_from_request

logger = logging.getLogger("middleware.access_handler")


class AccessHandlerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, path_config: EndpointConfig, get_database_session):
        super().__init__(app)
        self.path_config = path_config
        self.get_database_session = get_database_session

    async def dispatch(self, request: Request, call_next):
        logger.info("access_handler.dispatch()")
        pathInfo = self.path_config.get_path_info(request.url.path, request.method)
        
        if pathInfo is None:
            return Response(status_code=401)
            
        # all cred
        credentials = await extract_role_credentials_from_request(request)
        
        admintoken  = credentials.admintoken
        groupid     = credentials.groupid
        editid      = credentials.editid
        
        # user id from jwt
        userid = None
        try:
            userid = jwt.read_jwt(credentials.jwt)
        except Exception as e:            
            userid = None
            
        
        # Datenbank-Sitzung verwenden
        database_session_generator = self.get_database_session()
        database_session = next(database_session_generator)

        role = Role(role_infos=RoleInfos(admintoken=admintoken, userid=userid, groupid=groupid, editid=editid), db_session=database_session)
        logger.info(f"access_handler.dispatch(): {role._role.name}")
        
        # Prüfen, ob die Rolle Zugriff hat
        if role.hasAccess(pathInfo) is False:
            log_access(request.url.path, 403, 0.0000, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"Role conflict! Role: {role._role}, Required: {pathInfo.role}")
            return Response(status_code=403)

        # Wenn Zugriff gewährt wird, fortfahren
        return await call_next(request)